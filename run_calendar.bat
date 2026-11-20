@echo off
setlocal
cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
    echo uv is required to set up Calendar Weeks. Install uv and run this file again.
    exit /b 1
)

if not exist "%~dp0.venv\Scripts\pythonw.exe" (
    uv sync --project "%~dp0"
    if errorlevel 1 exit /b 1
)

start "" "%~dp0.venv\Scripts\pythonw.exe" -m calendar_weeks
