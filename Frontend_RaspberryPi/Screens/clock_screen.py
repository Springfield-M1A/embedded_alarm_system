from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
import datetime
import threading
from Services.memo_loader import get_regular_memo, get_date_memos
from Services.weather_api import get_weather
from Services.alarm_manager import get_regular_alarms, get_temporary_alarm

class ClockScreen(QWidget):
    data_updated = pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setStyleSheet("background-color: black; color: white;")
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        self.setLayout(self.layout)

        # Date / Time
        self.date_label = QLabel("")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("font-size: 22px; color: white;")
        self.layout.addWidget(self.date_label)

        self.time_label = QLabel("")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font-size: 100px; color: white; font-weight: bold;")
        self.layout.addWidget(self.time_label)

        # Weather / Fine Dust
        weather_dust_layout = QHBoxLayout()
        self.weather_label = QLabel("")
        self.weather_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.weather_label.setStyleSheet("font-size: 18px; color: white;")
        weather_dust_layout.addWidget(self.weather_label)

        self.dust_label = QLabel("")
        self.dust_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dust_label.setStyleSheet("font-size: 18px; color: white;")
        weather_dust_layout.addWidget(self.dust_label)

        self.layout.addLayout(weather_dust_layout)

        # Memo Box
        self.memo_box = QWidget()
        self.memo_box.setStyleSheet("""
            background-color: #222;
            border: 1px solid #555;
            border-radius: 10px;
            padding: 10px;
        """)
        memo_layout = QVBoxLayout()
        memo_layout.setSpacing(5)
        self.memo_box.setLayout(memo_layout)

        self.memo_regular_label = QLabel("")
        self.memo_regular_label.setStyleSheet("font-size: 18px; color: white;")
        self.memo_regular_label.setWordWrap(True)
        memo_layout.addWidget(self.memo_regular_label)

        self.date_memo_label = QLabel("")
        self.date_memo_label.setStyleSheet("font-size: 18px; color: white; border-top: 1px solid #555; padding-top: 5px;")
        self.date_memo_label.setWordWrap(True)
        memo_layout.addWidget(self.date_memo_label)

        self.layout.addWidget(self.memo_box)

        # Alarm Box
        self.alarm_box = QWidget()
        self.alarm_box.setStyleSheet("""
            background-color: #222;
            border: 1px solid #555;
            border-radius: 10px;
            padding: 10px;
        """)
        alarm_layout = QVBoxLayout()
        alarm_layout.setSpacing(5)
        self.alarm_box.setLayout(alarm_layout)

        self.alarm_regular_label = QLabel("")
        self.alarm_regular_label.setStyleSheet("font-size: 18px; color: white;")
        self.alarm_regular_label.setWordWrap(True)
        alarm_layout.addWidget(self.alarm_regular_label)

        self.alarm_temp_label = QLabel("")
        self.alarm_temp_label.setStyleSheet("font-size: 18px; color: white; border-top: 1px solid #555; padding-top: 5px;")
        self.alarm_temp_label.setWordWrap(True)
        alarm_layout.addWidget(self.alarm_temp_label)

        self.layout.addWidget(self.alarm_box)

        # Cache
        self.weather_cache = {'weather': '-', 'temperature': '-', 'dust': '-'}
        self.memo_cache = {'regular': '', 'date_memos': {}}
        self.alarm_cache = {'regular': [], 'temp': None}

        self.data_updated.connect(self.update_info)

        # Clock timer (1s)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time_only)
        self.timer.start(1000)
        self.update_time_only()

        # Full data timer (60s)
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.fetch_all_async)
        self.data_timer.start(60000)
        self.fetch_all_async()  # Initial load

        # Temporary alarm refresh (10s)
        self.temp_alarm_timer = QTimer()
        self.temp_alarm_timer.timeout.connect(self.fetch_temp_alarm_only)
        self.temp_alarm_timer.start(10000)
        self.fetch_temp_alarm_only()

    def update_time_only(self):
        now = datetime.datetime.now()
        self.date_label.setText(now.strftime("%Y-%m-%d (%A)"))
        self.time_label.setText(now.strftime("%H:%M:%S"))

    def fetch_all_async(self):
        def run():
            weather = get_weather()
            regular_memo = get_regular_memo()
            date_memos = get_date_memos()
            regular_alarms = get_regular_alarms()
            temp_alarm = get_temporary_alarm()
            self.weather_cache = weather
            self.memo_cache = {
                "regular": regular_memo,
                "date_memos": date_memos,
            }
            self.alarm_cache = {
                "regular": regular_alarms,
                "temp": temp_alarm,
            }
            self.data_updated.emit()
        threading.Thread(target=run).start()

    def fetch_temp_alarm_only(self):
        def run():
            temp_alarm = get_temporary_alarm()
            self.alarm_cache["temp"] = temp_alarm
            self.data_updated.emit()
        threading.Thread(target=run).start()

    def update_info(self):
        w = self.weather_cache
        self.weather_label.setText(f"☁ Weather: {w['weather']} {w['temperature']}")
        self.dust_label.setText(f"🌫 Fine Dust: {w['dust']}")

        regular_memo = self.memo_cache["regular"]
        if regular_memo:
            self.memo_regular_label.setText(f"✓ Regular Memo: {regular_memo}")
        else:
            self.memo_regular_label.setText("✓ Regular Memo: None")

        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        date_memos = self.memo_cache["date_memos"]
        if today in date_memos:
            self.date_memo_label.setText(f"🗓 Today's Memo: {date_memos[today]}")
        else:
            next_memo = None
            next_date = None
            for date in sorted(date_memos.keys()):
                if date > today:
                    next_memo = date_memos[date]
                    next_date = date
                    break
            if next_memo:
                self.date_memo_label.setText(f"🗓 Upcoming Memo ({next_date}): {next_memo}")
            else:
                self.date_memo_label.setText("🗓 No Upcoming Memos")

        alarms = self.alarm_cache["regular"]
        if alarms:
            alarm_texts = [f"{time} ({label})" for time, label in alarms]
            self.alarm_regular_label.setText("🔔 Regular Alarms: " + ", ".join(alarm_texts))
        else:
            self.alarm_regular_label.setText("🔔 No Regular Alarms")

        temp_alarm = self.alarm_cache["temp"]
        if temp_alarm:
            self.alarm_temp_label.setText(f"⏰ Temporary Alarm: {temp_alarm}")
        else:
            self.alarm_temp_label.setText("⏰ No Temporary Alarm")