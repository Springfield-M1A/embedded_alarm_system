import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget
from PyQt6.QtCore import Qt
from Screens.clock_screen import ClockScreen
from Screens.alarm_set_screen import AlarmSetScreen
from Screens.alarm_ring_screen import AlarmRingScreen
from Screens.memo_check_screen import MemoCheckScreen
from Services.memo_loader import get_regular_memo
import requests

class SmartAlarmApp(QStackedWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Smart Alarm IoT")
        self.setFixedSize(700, 500)
        self.setStyleSheet("background-color: black;")

        # Register screens
        self.clock_screen = ClockScreen(self)
        self.alarm_set_screen = AlarmSetScreen(self)
        self.memo_check_screen = MemoCheckScreen(self)
        self.alarm_ring_screen = AlarmRingScreen(self)

        self.screens = [self.clock_screen, self.alarm_set_screen, self.memo_check_screen]
        self.current_index = 0

        for screen in self.screens:
            self.addWidget(screen)

        self.addWidget(self.alarm_ring_screen)
        self.setCurrentWidget(self.screens[0])

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Left:
            self.current_index = (self.current_index - 1) % len(self.screens)
            self.setCurrentWidget(self.screens[self.current_index])
            print(f"Moved to previous screen: {self.current_index}")
        elif key == Qt.Key.Key_Right:
            self.current_index = (self.current_index + 1) % len(self.screens)
            self.setCurrentWidget(self.screens[self.current_index])
            print(f"Moved to next screen: {self.current_index}")
        elif key == Qt.Key.Key_Tab:
            if self.currentWidget() == self.clock_screen:
                self.setCurrentWidget(self.alarm_ring_screen)
                print("Switched to alarm ringing screen")
            else:
                self.setCurrentWidget(self.clock_screen)
                print("Switched to clock screen")
        else:
            # Forward other keys to the current screen
            current_screen = self.currentWidget()
            if hasattr(current_screen, "keyPressEvent"):
                current_screen.keyPressEvent(event)


if __name__ == "__main__":
    print(requests.get("http://127.0.0.1:5000/api/weather").json())
    app = QApplication(sys.argv)
    window = SmartAlarmApp()
    window.show()
    sys.exit(app.exec())