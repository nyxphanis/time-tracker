import tkinter as tk
from utils import load_data, round_minutes, export_report, update_total_hours
from datetime import datetime
import pandas as pd

DATA_FILE = "time_tracking_data.csv"

class TimeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Tracker v1")
        self.data = load_data(DATA_FILE)
        self.start_time = None

        # GUI Components
        self.task_entry = tk.Entry(root, width=30)
        self.task_entry.pack()
        self.start_button = tk.Button(root, text="Start Task", command=self.start_task)
        self.start_button.pack()
        self.stop_button = tk.Button(root, text="Stop Task", command=self.stop_task, state="disabled")
        self.stop_button.pack()
        self.export_button = tk.Button(root, text="Export Report", command=lambda: export_report(self.data))
        self.export_button.pack()

    def start_task(self):
        task_name = self.task_entry.get()
        if not task_name:
            tk.messagebox.showerror("Error", "Please enter a task name.")
            return
        self.start_time = datetime.now()

    def stop_task(self):
        if self.start_time is None:
            tk.messagebox.showerror("Error", "No task is running.")
            return
        end_time = datetime.now()
        task_name = self.task_entry.get()
        time_diff = end_time - self.start_time
        rounded_minutes = round_minutes(time_diff)
        new_task = pd.DataFrame([{"Task": task_name, "Start": self.start_time, "End": end_time, "Duration (Minutes)": rounded_minutes}])
        self.data = pd.concat([self.data, new_task])
        self.data.to_csv(DATA_FILE, index=False)
        self.start_time = None

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()

def run():
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()