import pandas as pd
from datetime import timedelta
from tkinter import filedialog, messagebox

def load_data(data_file):
    try:
        data = pd.read_csv(data_file)
        if not all(col in data.columns for col in ["Task", "Start", "End", "Duration (Minutes)"]):
            raise ValueError("CSV is missing required columns.")
    except (FileNotFoundError, ValueError):
        data = pd.DataFrame(columns=["Task", "Start", "End", "Duration (Minutes)"])
    return data

def round_minutes(time_diff):
    """Rounds the time difference to the nearest minute."""
    seconds = time_diff.total_seconds()
    minutes = seconds / 60
    return int(minutes + 0.5)  # Round to nearest integer

def export_report(data):
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if save_path:
        data.to_csv(save_path, index=False)
        messagebox.showinfo("Export", "Report exported successfully!")

def update_total_hours(data):
    """Calculate and return total hours worked."""
    total_minutes = data["Duration (Minutes)"].sum()
    total_hours = total_minutes / 60
    return total_hours
