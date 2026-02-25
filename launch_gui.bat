@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  set "PYTHON_CMD=py -3"
) else (
  set "PYTHON_CMD=python"
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 goto :fail
)

echo Installing/updating dependencies...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :fail

echo Starting GUI...
.venv\Scripts\python.exe bingo_gui.py
if errorlevel 1 goto :fail
exit /b 0

:fail
echo Failed to start Bingo GUI.
exit /b 1
