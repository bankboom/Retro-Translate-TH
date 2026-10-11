@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 "tools\install_once.py" install
) else (
  python "tools\install_once.py" install
)
if errorlevel 1 (
  echo Installation failed. Read docs\INSTALL_ONCE_TH.md
  pause
  exit /b 1
)
echo.
echo Installation complete. Open %USERPROFILE%\RetroThaiProjects in Codex and start a new chat.
pause
