@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d %~dp0

set "APP_DIR=%~dp0"
set "APP_ENTRY=-m src.fantasy_optimizer.web_app"
set "PYEXE=%~dp0.venv\Scripts\python.exe"
set "APP_TITLE=Fantasy Optimizer"
set "APP_BUILD=2026-08-20-chart-refresh"

rem The Lab is the live UI served on port 5000. Keep a workspace fallback for clean installs.
set "LAB_DIR=C:\Users\zaire\Downloads\football_tingz-main\football_tingz-main"
if exist "%LAB_DIR%\app.py" if exist "%LAB_DIR%\.venv\Scripts\python.exe" (
  set "APP_DIR=%LAB_DIR%"
  set "APP_ENTRY=app.py"
  set "PYEXE=%LAB_DIR%\.venv\Scripts\python.exe"
  set "APP_TITLE=The Lab"
)

if not exist "%PYEXE%" (
  echo Python executable not found: %PYEXE%
  echo Create the project virtual environment before starting the web app.
  exit /b 1
)

:restart
netstat -ano | findstr /r /c:":5000 .*LISTENING" >nul 2>&1
if not errorlevel 1 (
  powershell -NoProfile -Command "try { $response = Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 'http://127.0.0.1:5000/'; if ($response.StatusCode -eq 200 -and $response.Content -match '<title>\s*%APP_TITLE%\s*</title>' -and $response.Content -match 'data-app-build=\"%APP_BUILD%\"') { exit 0 }; exit 1 } catch { exit 1 }" >nul 2>&1
  if not errorlevel 1 (
    echo Web app is already available at http://127.0.0.1:5000/
    timeout /t 5 /nobreak >nul
    goto restart
  )
  echo Port 5000 is in use but is not serving the Fantasy Web App.
  echo Stop the conflicting process, then the launcher will start the app.
  timeout /t 5 /nobreak >nul
  goto restart
)

echo Starting web app from "%APP_DIR%" on http://127.0.0.1:5000/
pushd "%APP_DIR%"
if /i "%APP_ENTRY%"=="app.py" (
  "%PYEXE%" app.py
) else (
  "%PYEXE%" %APP_ENTRY%
)
set EXITCODE=%ERRORLEVEL%
popd
echo Web app exited with code %EXITCODE%. Restarting in 2 seconds...
timeout /t 2 /nobreak >nul
goto restart
