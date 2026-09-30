@echo off
setlocal

rem Launch the notebook from this folder and open it in the default browser.
rem The server listens only on the local machine and uses no login token.
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -m jupyter notebook ^
        --notebook-dir="%~dp0" ^
        --ip=127.0.0.1 ^
        --ServerApp.token="" ^
        --ServerApp.password="" ^
        --ServerApp.allow_remote_access=False ^
        --ServerApp.open_browser=True ^
        "%~dp0Max2SAT.ipynb"
    goto :end
)

python -m jupyter notebook ^
    --notebook-dir="%~dp0" ^
    --ip=127.0.0.1 ^
    --ServerApp.token="" ^
    --ServerApp.password="" ^
    --ServerApp.allow_remote_access=False ^
    --ServerApp.open_browser=True ^
    "%~dp0Max2SAT.ipynb"

:end
pause
