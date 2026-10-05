@echo off
TITLE STARK - Auto Execution
color 0a

echo.
echo ==================================================
echo      STARTING JOB APPLICATION PROTOCOL...
echo ==================================================
echo.

py run.py

IF %ERRORLEVEL% NEQ 0 (
    python run.py
)

echo.
echo ==================================================
echo      PROCESS COMPLETE
echo ==================================================
pause