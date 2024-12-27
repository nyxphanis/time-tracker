import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
from datetime import datetime

# Data Storage File
DATA_FILE = "time_tracking_data.csv"

# Initialize Data
try:
    data = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    data = pd.DataFrame(columns=["Task", "Start", "End"])

# Start Task Function
def start_task():
    global start_time
    task_name = task_entry.get()
    if not task_name:
        messagebox.showerror("Error", "Task name is required!")
        return
    start_time = datetime.now()
    task_label.config(text=f"Task: {task_name}")
    status_label.config(text="Status: Running")
    start_button.config(state="disabled")
    stop_button.config(state="normal")

# Stop Task Function
def stop_task():
    global start_time
    if start_time is None:
        messagebox.showerror("Error", "No task is running!")
        return
    end_time = datetime.now()
    task_name = task_entry.get()
    global data
    data = pd.concat([data, pd.DataFrame([{
        "Task": task_name,
        "Start": start_time,
        "End": end_time
    }])])
    data.to_csv(DATA_FILE, index=False)
    task_label.config(text="Task: None")
    status_label.config(text="Status: Stopped")
    start_button.config(state="normal")
    stop_button.config(state="disabled")

# Export Report
def export_report():
    save_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
    if save_path:
        data.to_csv(save_path, index=False)
        messagebox.showinfo("Export", "Report exported successfully!")

# GUI Setup
app = tk.Tk()
app.title("Time Tracking App")

task_label = tk.Label(app, text="Task: None")
task_label.pack()

status_label = tk.Label(app, text="Status: Stopped")
status_label.pack()

task_entry = tk.Entry(app, width=30)
task_entry.pack()

start_button = tk.Button(app, text="Start Task", command=start_task)
start_button.pack()

stop_button = tk.Button(app, text="Stop Task", command=stop_task, state="disabled")
stop_button.pack()

export_button = tk.Button(app, text="Export Report", command=export_report)
export_button.pack()

app.mainloop()
