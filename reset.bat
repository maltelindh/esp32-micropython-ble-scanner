@echo off
REM Soft reset the ESP32
REM Change MPREMOTE_PORT to your COM port if auto-detection fails (e.g., COM5)
set MPREMOTE_PORT=auto

echo Soft-resetting ESP32...
mpremote connect %MPREMOTE_PORT% soft-reset
echo Done.
