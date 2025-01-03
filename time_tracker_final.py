import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
    QFileDialog,
)
from PyQt5.QtCore import QTimer
from datetime import datetime
import pandas as pd
import numpy as np


DATA_FILE = "time_tracking_data.csv"


def load_data(data_file):
    """Load the tracking data from a CSV file or create an empty DataFrame with predefined columns and types."""
    required_columns = {
        "User": pd.StringDtype(),  # Use pandas string type for text
        "Start": "datetime64[ns]",  # Specific datetime type
        "End": "datetime64[ns]",    # Specific datetime type
        "Duration": np.float64      # Number type for duration
    }

    try:
        # Load the data
        data = pd.read_csv(data_file)

        # Ensure all required columns are present
        for col, dtype in required_columns.items():
            if col not in data.columns:
                data[col] = pd.Series(dtype=dtype)  # Add missing columns with specific dtype

        # Convert "Start" and "End" columns to datetime objects
        data["Start"] = pd.to_datetime(data["Start"], errors="coerce")
        data["End"] = pd.to_datetime(data["End"], errors="coerce")

        # Drop any extra columns that are not required (optional)
        data = data[required_columns.keys()]

    except (FileNotFoundError, pd.errors.ParserError):
        # Create an empty DataFrame with the required columns and dtypes
        data = pd.DataFrame(columns=required_columns.keys()).astype(required_columns)

    return data

class TimeTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Tracker v2")
        self.setFixedSize(400, 350)  # Set fixed size for the window
        self.data = load_data(DATA_FILE)  # Load the data into a single DataFrame
        self.start_time = None

        # Get the current Windows username
        self.username = os.getlogin()

        # GUI Components
        self.start_button = QPushButton("Start Task", self)
        self.stop_button = QPushButton("Stop Task", self)
        self.export_button = QPushButton("Export Report", self)
        self.status_label = QLabel("Status: Not Tracking", self)
        self.time_label = QLabel("", self)  # Label to show current date and time
        self.username_label = QLabel(f"User: {self.username}", self)

        # Layout
        layout = QVBoxLayout()
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

        # Disable stop button initially
        self.stop_button.setEnabled(False)

        # Apply custom styling
        self.apply_styles()

        # Set up a timer to update the time every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def apply_styles(self):
        self.setStyleSheet(
            """
            QWidget {
                background-color: #F7F7F7;
                border-radius: 10px;
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
        """
        )

    def update_time(self):
        """Update the time label every second."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"Current Time: {current_time}")

    def start_task(self):
        self.start_time = datetime.now()
        self.status_label.setText("Status: Tracking...")
        self.stop_button.setEnabled(True)
        self.start_button.setText("Tracking...")  # Update button text
        self.start_button.setStyleSheet("background-color: #e68a2e;")  # Change color

    def stop_task(self):
        if self.start_time is None:
            QMessageBox.critical(self, "Error", "No task is running.")
            return

        end_time = datetime.now()
        time_diff = end_time - self.start_time

        # Calculate fractional hours directly from time_diff
        fractional_hours = round(time_diff.total_seconds() / 3600, 2)

        # Define session data
        session_data = pd.DataFrame(
            [
                {
                    "User": self.username,
                    "Start": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "End": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Duration": fractional_hours,
                }
            ]
        )

        # Ensure the data has the same columns
        self.data = pd.concat([self.data, session_data], ignore_index=True)

        # Save to CSV
        try:
            self.data.to_csv(DATA_FILE, index=False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {e}")
            return

        # Reset the tracker
        self.start_time = None
        self.status_label.setText("Status: Not Tracking")
        self.stop_button.setEnabled(False)
        self.start_button.setText("Start Task")  # Reset button text
        self.start_button.setStyleSheet(
            """
            QPushButton {
                background-color: #F1A337;
                /* ... (other styles) */
            }
            QPushButton:hover {
                background-color: #e68a2e;
            }
        """
        )  # Reset color

    def export_report(self):
        """Exports the report to a CSV file."""
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "", "CSV files (*.csv)"
        )
        if save_path:
            self.data.to_csv(save_path, index=False)
            QMessageBox.information(self, "Export", "Report exported successfully!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeTrackerApp()
    window.show()
    sys.exit(app.exec_())