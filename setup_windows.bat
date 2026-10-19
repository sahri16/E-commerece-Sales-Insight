@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 -m venv .venv
if errorlevel 1 goto failed
goto install
:usepython
python -m venv .venv
if errorlevel 1 goto failed
:install
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Setup complete. Double-click start_windows.bat to open the dashboard.
pause
exit /b 0
:failed
echo Setup failed. Install Python 3.11 or 3.12 from python.org and enable Add Python to PATH.
echo Check your internet connection and read docs/START_HERE_ROMAN_URDU.md.
pause
exit /b 1
