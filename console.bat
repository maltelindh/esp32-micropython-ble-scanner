@echo off
REM Open REPL console
REM Change MPREMOTE_PORT to your COM port if auto-detection fails (e.g., COM5)
set MPREMOTE_PORT=auto

echo Opening REPL console...
mpremote connect %MPREMOTE_PORT% repl
