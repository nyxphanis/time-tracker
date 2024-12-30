import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QTimer
from utils import load_data, round_minutes, export_report, update_total_hours
from datetime import datetime
import pandas as pd

DATA_FILE = "time_tracking_data.csv"


class TimeTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Tracker v1")
        self.setFixedSize(400, 350)  # Set fixed size for the window
        self.data = load_data(DATA_FILE)
        self.start_time = None

        # Get the current Windows username
        self.username = os.getlogin()

        # GUI Components
        self.task_entry = QLineEdit(self)
        self.task_entry.setPlaceholderText("Enter task name")
        self.start_button = QPushButton("Start Task", self)
        self.stop_button = QPushButton("Stop Task", self)
        self.export_button = QPushButton("Export Report", self)
        self.status_label = QLabel("Status: Not Tracking", self)
        self.time_label = QLabel("", self)  # Label to show current date and time
        self.username_label = QLabel(f"User: {self.username}", self)


        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.task_entry)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.export_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.time_label)
        layout.addWidget(self.username_label)
        self.setLayout(layout)

        # Button actions
        self.start_button.clicked.connect(self.start_task)
        self.stop_button.clicked.connect(self.stop_task)
        self.export_button.clicked.connect(self.export_report)
       # self.export_button.clicked.connect(lambda: export_report(self.data))

        # Disable stop button initially
        self.stop_button.setEnabled(False)

        # Apply custom styling
        self.apply_styles()

        # Set up a timer to update the time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def apply_styles(self):
        # Set stylesheet for the window
        self.setStyleSheet("""
                  QWidget {
                      background-color: #F7F7F7;
                      border-radius: 10px;
                  }
                  QLineEdit {
                      background-color: #FFF;
                      border: 2px solid #F1A337;
                      border-radius: 10px;
                      padding: 5px;
                      font-size: 16px;
                  }
                  QPushButton {
                      background-color: #F1A337;
                      color: white;
                      border: 2px solid #F1A337;
                      border-radius: 10px;
                      padding: 10px;
                      font-size: 16px;
                      margin: 5px;
                  }
                  QPushButton:hover {
                      background-color: #e68a2e;
                  }
                  QLabel {
                      font-size: 18px;
                      color: #333;
                      font-weight: bold;
                  }
                  QVBoxLayout {
                      margin: 20px;
                  }
              """)

    def update_time(self):
        """Update the time label every second."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"Current Time: {current_time}")

    def start_task(self):
        task_name = self.task_entry.text()
        if not task_name:
            QMessageBox.critical(self, "Error", "Please enter a task name.")
            return
        self.start_time = datetime.now()
        self.status_label.setText("Status: Tracking...")
        self.stop_button.setEnabled(True)

    def stop_task(self):
        if self.start_time is None:
            QMessageBox.critical(self, "Error", "No task is running.")
            return
        end_time = datetime.now()
        task_name = self.task_entry.text()
        time_diff = end_time - self.start_time
        rounded_minutes = round_minutes(time_diff)
        new_task = pd.DataFrame([{
            "Task": task_name,
            "Start": self.start_time,
            "End": end_time,
            "Duration (Minutes)": rounded_minutes,
            "User":self.username
        }])
        self.data = pd.concat([self.data, new_task])
        self.data.to_csv(DATA_FILE, index=False)
        self.start_time = None
        self.status_label.setText("Status: Not Tracking")
        self.stop_button.setEnabled(False)

    def export_report(self):
        # Add the username when exporting
        self.data['User'] = self.username
        export_report(self.data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeTrackerApp()
    window.show()
    sys.exit(app.exec_())
