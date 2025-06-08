from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QUrl, pyqtSignal
from PyQt6.QtMultimedia import QSoundEffect
import datetime
import os
import threading

from Services.memo_loader import get_regular_memo, get_date_memo


def monitor_stretch_motion():
    try:
        import cv2
        import mediapipe as mp
        import time

        mp_pose = mp.solutions.pose
        cap = cv2.VideoCapture(0)

        detected_start_time = None
        stretch_confirmed = False
        min_duration = 0.5

        with mp_pose.Pose(min_detection_confidence=0.5) as pose:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    lw = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
                    rw = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
                    nose = landmarks[mp_pose.PoseLandmark.NOSE]

                    stretch_condition = lw.y < nose.y and rw.y < nose.y

                    if stretch_condition:
                        if detected_start_time is None:
                            detected_start_time = time.time()
                        elif time.time() - detected_start_time >= min_duration:
                            stretch_confirmed = True
                    else:
                        detected_start_time = None

                    if stretch_confirmed:
                        print("Stretch Detected!")
                        break

        cap.release()
        return stretch_confirmed

    except Exception as e:
        print(f"[Stretch Detection Error] {e}")
        return False


class AlarmRingScreen(QWidget):
    memo_updated = pyqtSignal()
    stop_alarm_signal = pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setStyleSheet("background-color: black; color: white;")

        self.init_ui()
        self.memo_cache = {"regular": "", "date": ""}
        self.setup_timers()
        self.sound = None
        self.setup_sound()

        self.stop_alarm_signal.connect(self.stop_alarm)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(30)
        self.setLayout(layout)

        self.icon_label = QLabel("🔔")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 200px;")
        layout.addWidget(self.icon_label)

        self.time_label = QLabel("")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font-size: 60px;")
        layout.addWidget(self.time_label)

        self.memo_box = QWidget()
        self.memo_box.setStyleSheet("""
            background-color: #222;
            border: 1px solid #555;
            border-radius: 10px;
            padding: 10px;
        """)
        memo_layout = QVBoxLayout(self.memo_box)
        memo_layout.setSpacing(5)

        self.memo_regular_label = QLabel("")
        self.memo_regular_label.setStyleSheet("font-size: 18px; color: white;")
        memo_layout.addWidget(self.memo_regular_label)

        self.date_memo_label = QLabel("")
        self.date_memo_label.setStyleSheet("font-size: 18px; color: white; border-top: 1px solid #555; padding-top: 5px;")
        memo_layout.addWidget(self.date_memo_label)

        layout.addWidget(self.memo_box)

    def setup_timers(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

        self.memo_timer = QTimer()
        self.memo_timer.timeout.connect(self.fetch_memo_async)
        self.memo_timer.start(30000)
        self.memo_updated.connect(self.update_memo)
        self.fetch_memo_async()

    def setup_sound(self):
        try:
            sound_path = os.path.join("Frontend_RaspberryPi", "Assets", "alarm.wav")
            if os.path.exists(sound_path):
                self.sound = QSoundEffect()
                self.sound.setSource(QUrl.fromLocalFile(os.path.abspath(sound_path)))
                self.sound.setLoopCount(999999)
                self.sound.setVolume(0.5)
            else:
                print(f"[Alarm Sound] File not found: {sound_path}")
        except Exception as e:
            print(f"[Alarm Sound Setup Error] {e}")

    def start_alarm(self):
        print("Alarm started!")
        if self.sound:
            self.sound.play()
        else:
            print("[Warning] Alarm sound not available")

        threading.Thread(target=self.monitor_stretch_motion_thread, daemon=True).start()

    def monitor_stretch_motion_thread(self):
        if monitor_stretch_motion():
            self.stop_alarm_signal.emit()

    def update_time(self):
        now = datetime.datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))

    def fetch_memo_async(self):
        def run():
            try:
                regular = get_regular_memo()
                date = get_date_memo()
                self.memo_cache["regular"] = regular or "None"
                self.memo_cache["date"] = date or "None"
                self.memo_updated.emit()
            except Exception as e:
                print(f"[Memo Fetch Error] {e}")
                self.memo_cache["regular"] = "Load failed"
                self.memo_cache["date"] = "Load failed"
                self.memo_updated.emit()
        threading.Thread(target=run, daemon=True).start()

    def update_memo(self):
        self.memo_regular_label.setText(f"✓ Regular Memo: {self.memo_cache['regular']}")
        self.date_memo_label.setText(f"🗓 Date Memo: {self.memo_cache['date']}")

    def stop_alarm(self):
        print("Alarm stopped!")
        if self.sound:
            self.sound.stop()
        self.setup_sound()
        self.controller.setCurrentWidget(self.controller.clock_screen)
        print("Switched to clock screen")

    def showEvent(self, event):
        super().showEvent(event)
        self.start_alarm()

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Escape):
            self.stop_alarm()
        else:
            super().keyPressEvent(event)