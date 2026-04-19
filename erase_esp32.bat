@echo off
REM Erase all files from ESP32 root directory
REM Change MPREMOTE_PORT to your COM port if auto-detection fails (e.g., COM5)
set MPREMOTE_PORT=auto

echo WARNING: This will delete ALL files from the ESP32 root directory!
set /p confirm="Continue? (y/n): "

if /i not "%confirm%"=="y" (
    echo Cancelled.
    exit /b 0
)

echo.
echo Erasing ESP32...
mpremote connect %MPREMOTE_PORT% fs rm *

echo.
echo Done.

