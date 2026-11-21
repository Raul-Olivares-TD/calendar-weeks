# 📅 Calendar Weeks

A lightweight desktop utility built with Python and Qt (PySide) that displays the current week number directly in your Windows system tray / notification area.

---

## 🚀 Quick Start (End Users — Portable Windows Release)

If you downloaded the packaged `.zip` from the [Releases](../../releases) page, **you do not need Python installed on your system**. Everything runs self-contained inside the extracted folder.

### 1. Installation
1. Extract the `.zip` archive to your preferred location (e.g., `C:\Apps\CalendarWeeks`).
2. Open the `utils` folder and double-click **`installer.bat`**.
   * *This downloads a portable Python runtime locally, installs dependencies, creates the desktop/root shortcut with the app icon, registers the app in Windows Startup, and launches it automatically.*

### 2. Running the App
* Double-click the **`Calendar Weeks`** shortcut created in the root folder (or run `utils\run_calendar.bat`).
* The app will also start automatically in the system tray every time you log in to Windows.

### 3. Uninstallation
* Open the `utils` folder and double-click **`uninstaller.bat`**.
* *This stops the background process, removes the Windows Startup shortcut, and deletes the entire application folder cleanly without leaving any leftover files or registry entries.*

---

## 🛠️ Developer Workflow (Running from Source with `uv`)

If you want to run, modify, or contribute to the source code, this project uses **[`uv`](https://astral.sh)** for fast Python and dependency management.

### Prerequisites
* [Git](https://git-scm.com)
* [uv](https://astral.shgetting-started/installation/) installed on your machine

### 1. Clone the Repository
```bash
git clone https://github.com
cd calendar_weeks
```

### 2. Sync Dependencies
Create the `.venv` virtual environment and install all locked dependencies automatically:
```bash
uv sync
```

### 3. Run the Application
You can launch the application directly through `uv` using the configured entry point:
```bash
uv run calendar-weeks
```

Alternatively, you can run it as a module or use the root batch script on Windows:
```bash
uv run python -m calendar_weeks
```
or
```bat
run_calendar.bat
```

---

## 📂 Repository Structure

```text
calendar_weeks/
├── src/
│   └── calendar_weeks/
│       ├── __init__.py
│       ├── __main__.py            # Module entry point
│       ├── calendar.py            # Main application logic (calendar_weeks.calendar:main)
│       ├── calendar_icon_tray.ico # Windows shortcut & tray icon
│       ├── calendar_icon_tray.png # Tray icon asset
│       ├── actualizar.png         # Refresh UI icon
│       ├── cerrar2.png            # Close UI icon
│       └── style.qss              # Qt Style Sheet
├── tests/                         # Test suite
├── .gitignore
├── .python-version                # Pinned Python version
├── pyproject.toml                 # Project metadata, scripts & dependencies
├── uv.lock                        # Locked dependency versions
├── run_calendar.bat               # Quick launcher script
└── README.md
```

---

## 📝 Common `uv` Commands Cheatsheet

| Task | Command |
| :--- | :--- |
| **Install / update environment** | `uv sync` |
| **Run the application** | `uv run calendar-weeks` |
| **Run test suite** | `uv run pytest` |
| **Add a new dependency** | `uv add <package-name>` |
| **Remove a dependency** | `uv remove <package-name>` |
