import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QFileDialog,
    QDialog,
    QFormLayout,
    QDateEdit,
    QLineEdit,
)
from PyQt6.QtCore import QTimer, QDate
from datetime import datetime
import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Protection
from openpyxl.utils import get_column_letter

def app_dir():
    """Folder containing the app (source file or PyInstaller executable)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


# CSV lives next to the script or .exe (see app_dir), not the shell's working folder.
DATA_FILE = app_dir() / "time_tracking_data.csv"


def format_elapsed(seconds):
    """Format seconds as HH:MM:SS."""
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def load_data(data_file):
    """Load sessions from CSV, or start empty. Adds Task column for older files."""
    required_columns = {
        "User": pd.StringDtype(),
        "Start": "datetime64[ns]",
        "End": "datetime64[ns]",
        "Duration": np.float64,
        "Task": pd.StringDtype(),
    }
    try:
        data = pd.read_csv(data_file)
        for col, dtype in required_columns.items():
            if col not in data.columns:
                data[col] = pd.Series(dtype=dtype)
        data["Start"] = pd.to_datetime(data["Start"], errors="coerce")
        data["End"] = pd.to_datetime(data["End"], errors="coerce")
        data["Task"] = data["Task"].fillna("").astype(pd.StringDtype())
        data = data[list(required_columns.keys())]
    except (FileNotFoundError, pd.errors.ParserError):
        data = pd.DataFrame(columns=required_columns.keys()).astype(required_columns)
    return data


class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Report")
        self.setStyleSheet("""
            QDialog { background-color: #F7F7F7; }
            QLabel { font-size: 13px; color: #333333; font-weight: bold; }
            QDateEdit {
                color: #333333;
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 13px;
            }
            QCalendarWidget {
                background-color: #FFFFFF;
                color: #333333;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #F7F7F7;
                color: #333333;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #333333;
                background-color: #FFFFFF;
                selection-background-color: #F1A337;
                selection-color: #FFFFFF;
            }
            QPushButton {
                background-color: #F1A337;
                color: white;
                border: 1px solid #F1A337;
                border-radius: 6px;
                padding: 5px 14px;
                font-size: 13px;
                min-height: 26px;
            }
            QPushButton:hover { background-color: #e68a2e; }
        """)

        # Date From
        self.date_from_label = QLabel("Date From:")
        self.date_from_edit = QDateEdit()
        self.date_from_edit.setCalendarPopup(True)
        self.date_from_edit.setDate(QDate.currentDate().addDays(-30))  # Default: 30 days ago

        # Date To
        self.date_to_label = QLabel("Date To:")
        self.date_to_edit = QDateEdit()
        self.date_to_edit.setCalendarPopup(True)
        self.date_to_edit.setDate(QDate.currentDate())  # Default: Today

        # Export Button
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.accept)  # Connect to accept() slot

        # Layout
        layout = QFormLayout()
        layout.addRow(self.date_from_label, self.date_from_edit)
        layout.addRow(self.date_to_label, self.date_to_edit)
        layout.addRow(self.export_button)
        self.setLayout(layout)

    def get_date_range(self):
        date_from = self.date_from_edit.date()
        date_to = self.date_to_edit.date()
        return date_from, date_to


class StopTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stop Task")
        self.setMinimumWidth(320)
        self.setStyleSheet("""
            QDialog { background-color: #F7F7F7; }
            QLabel { font-size: 13px; color: #333333; font-weight: bold; }
            QLineEdit {
                color: #333333;
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #F1A337;
                color: white;
                border: 1px solid #F1A337;
                border-radius: 6px;
                padding: 5px 14px;
                font-size: 13px;
                min-height: 26px;
            }
            QPushButton:hover { background-color: #e68a2e; }
        """)

        self.task_label = QLabel("Task (optional):")
        self.task_edit = QLineEdit()
        self.task_edit.setPlaceholderText("What did you work on?")

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addWidget(self.cancel_button)
        buttons.addWidget(self.save_button)

        layout = QFormLayout()
        layout.addRow(self.task_label, self.task_edit)
        layout.addRow(buttons)
        self.setLayout(layout)

    def get_task(self):
        return self.task_edit.text().strip()


class TimeTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Tracker v2")
        self.setFixedSize(400, 320)
        self.data = load_data(DATA_FILE)
        self.start_time = None
        self.username = os.getlogin()

        # GUI Components
        self.start_button = QPushButton("Start Task", self)
        self.stop_button = QPushButton("Stop Task", self)
        self.export_button = QPushButton("Export Report", self)
        self.status_label = QLabel("Status: Not Tracking", self)
        self.elapsed_label = QLabel("Elapsed: —", self)
        self.time_label = QLabel("", self)
        self.username_label = QLabel(f"User: {self.username}", self)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.export_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.elapsed_label)
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
        self.setStyleSheet('''
        QWidget {
            background-color: #F7F7F7;
        }
        QPushButton {
            background-color: #F1A337;
            color: white;
            border: 1px solid #F1A337;
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 14px;
            margin: 3px;
            min-height: 28px;
        }
        QPushButton:hover {
            background-color: #e68a2e;
        }
        QLabel {
            font-size: 14px;
            color: #333333;
            font-weight: bold;
        }
        QLineEdit, QDateEdit {
            color: #333333;
            background-color: #FFFFFF;
            border: 1px solid #CCCCCC;
            border-radius: 4px;
            padding: 6px 8px;
            font-size: 14px;
            font-weight: normal;
            selection-color: #FFFFFF;
            selection-background-color: #F1A337;
        }
        QCalendarWidget {
            background-color: #FFFFFF;
            color: #333333;
        }
        QCalendarWidget QAbstractItemView:enabled {
            color: #333333;
            background-color: #FFFFFF;
            selection-background-color: #F1A337;
            selection-color: #FFFFFF;
        }
        QDialog {
            background-color: #F7F7F7;
        }
        QVBoxLayout {
            margin: 12px;
        }
        ''')

    def update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"Current Time: {current_time}")

        if self.start_time is not None:
            elapsed_sec = (datetime.now() - self.start_time).total_seconds()
            self.elapsed_label.setText(f"Elapsed: {format_elapsed(elapsed_sec)}")
        else:
            self.elapsed_label.setText("Elapsed: —")

    def closeEvent(self, event):
        # Stop the timer so Qt can exit cleanly (avoids noisy exit on Windows).
        self.timer.stop()
        event.accept()

    def start_task(self):
        # Ignore extra clicks while a session is already running.
        if self.start_time is not None:
            return

        self.start_time = datetime.now()
        self.status_label.setText("Status: Tracking...")
        self.elapsed_label.setText("Elapsed: 00:00:00")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.start_button.setText("Tracking...")
        self.start_button.setStyleSheet("background-color: #4CAF50;")
        print(f"START {datetime.now()}")


    def stop_task(self):
        if self.start_time is None:
            QMessageBox.critical(self, "Error", "No task is running.")
            return

        dialog = StopTaskDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        print(f"STOP {datetime.now()}")

        end_time = datetime.now()
        time_diff = end_time - self.start_time
        fractional_hours = round(time_diff.total_seconds() / 3600, 2)

        session_data = pd.DataFrame(
            [
                {
                    "User": self.username,
                    "Start": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "End": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Duration": fractional_hours,
                    "Task": dialog.get_task(),
                }
            ]
        )

        self.data = pd.concat([self.data, session_data], ignore_index=True)

        try:
            self.data.to_csv(DATA_FILE, index=False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data to {DATA_FILE}: {e}")
            return
        print(f"SAVE {datetime.now()}")

        self.start_time = None
        self.status_label.setText("Status: Not Tracking")
        self.elapsed_label.setText("Elapsed: —")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.start_button.setText("Start Task")
        self.start_button.setStyleSheet("background-color: #F1A337;")

    def export_report(self):
        export_dialog = ExportDialog(self)
        result = export_dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            date_from, date_to = export_dialog.get_date_range()
            if date_from.toPyDate() > date_to.toPyDate():
                QMessageBox.warning(
                    self,
                    "Invalid dates",
                    "Date From must be on or before Date To.",
                )
                return

            print(f"EXPORT HOURS {datetime.now()}")
            # Filter data based on the selected date range
            self.data["Start"] = pd.to_datetime(self.data["Start"], errors="coerce")
            #filtered_data = self.data[
               # (self.data["Start"].dt.date >= date_from) & (self.data["Start"].dt.date <= date_to)
               # (self.data["Start"].dt.date >= date_from.date()) & (self.data["Start"].dt.date <= date_to.date())
               # ]
            filtered_data = self.data[
                (self.data["Start"].dt.date >= date_from.toPyDate()) &
                (self.data["Start"].dt.date <= date_to.toPyDate())
                ]
            print(f"Date From: {type(date_from)}, Value: {date_from}")
            print(f"Date To: {type(date_to)}, Value: {date_to}")
            print(f"EXPORT HOURS {datetime.now()}")

            # Check if filtered data is empty
            if filtered_data.empty:
                QMessageBox.warning(self, "No Data", "No entries found for the selected dates.")
                return  # Stop further execution


            # Calculate total hours
            total_hours = filtered_data["Duration"].sum()


            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save Report", "", "Excel files (*.xlsx *.xlsm)"
            )
            if not save_path:
                return

            if not save_path.lower().endswith(('.xlsx', '.xlsm')):
                save_path += '.xlsx'

            try:
                export_to_protected_excel(filtered_data, total_hours, save_path)
                QMessageBox.information(
                    self, "Export", "Report exported successfully to a protected Excel file!"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export report: {e}")


def export_to_protected_excel(data, total_hours, save_path):
    """Write filtered sessions to Excel with a total row and sheet protection."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Time Tracking Report"

    # Add headers
    headers = list(data.columns)
    sheet.append(headers)

    # Add data rows
    for _, row in data.iterrows():
        sheet.append(list(row))

    # Add total hours row
    total_row = [""] * len(headers)
    total_row[0] = "Total Hours:"
    if "Duration" in headers:
        total_row[headers.index("Duration")] = total_hours
    sheet.append(total_row)

    # Formatting
    for col in range(1, len(headers) + 1):
        col_letter = get_column_letter(col)
        sheet.column_dimensions[col_letter].width = 18  # Adjust column width
        sheet.cell(row=1, column=col).style = "Accent1"  # Header style

    # Protect the sheet
    sheet.protection.sheet = True
    sheet.protection.password = "your_password"  # Set a password to protect the sheet

    # Lock all cells except those that need to be edited
    for row in sheet.iter_rows(min_row=2):  # Skip header row
        for cell in row:
            cell.protection = Protection(locked=True)

    workbook.save(save_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeTrackerApp()
    window.show()
    sys.exit(app.exec())