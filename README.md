# Time Tracker

Desktop app for tracking work hours. Logs sessions to a local CSV and can export filtered reports to Excel.

## Features

- Start / stop tasks with a running timer
- Optional task note when you stop (saved in the CSV)
- Local log file: `time_tracking_data.csv` (`User`, `Start`, `End`, `Duration`, `Task`)
- Export report for a date range as a protected `.xlsx` file

## Requirements

- Python **3.12** (recommended)
- See `requirements.txt`: PyQt6, pandas, openpyxl, numpy

## Setup

```powershell
cd D:\GitHub\time-tracker
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the app:

```powershell
.\.venv\Scripts\python.exe time_tracker_xls_date_sum.py
```

In PyCharm, set the interpreter to `.venv\Scripts\python.exe`.

If `python` is not on your PATH, always use the full path to `.venv\Scripts\python.exe` (same for `pip`).

## Usage

1. Click **Start Task** when you begin work.
2. Click **Stop Task** when you finish.
3. Optionally describe what you worked on, then **Save** (or **Cancel** to keep the timer running).
4. Use **Export Report** to pick a date range and save an Excel file.

`time_tracking_data.csv` is created in the same folder as the app (script or `.exe`).

## Build executable (Windows)

```powershell
cd D:\GitHub\time-tracker
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\python.exe -m PyInstaller --clean time_tracker_xls_date_sum.spec
```

Output: `dist\time_tracker_xls_date_sum.exe`

If the build fails on Qt plugins, try:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --clean --collect-all PyQt6 time_tracker_xls_date_sum.spec
```

## Git

Not tracked (see `.gitignore`): `.venv/`, `build/`, `dist/`, `time_tracking_data.csv`, `.idea/`
