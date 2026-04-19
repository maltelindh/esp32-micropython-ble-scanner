@echo off
setlocal enabledelayedexpansion

set MPREMOTE_PORT=auto

echo.
echo WARNING: This will delete ALL project files and directories from ESP32 root
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Aborted.
    exit /b 0
)

echo.
echo Listing files in root before delete...
mpremote connect %MPREMOTE_PORT% fs ls :

echo.
echo Deleting files and folders from ESP32 root...

REM Remove known files in root
for %%F in (
    boot.py
    main.py
    mqtt.py
    secrets.py
    updater.py
    version.json
    ble.py
    uping.py
) do (
    echo Removing %%F...
    mpremote connect %MPREMOTE_PORT% fs rm "%%F"
)

REM Remove known directories in root
for %%D in (
    lib
) do (
    echo Removing %%D recursively...
    mpremote connect %MPREMOTE_PORT% fs rm -r "%%D"
)

echo.
echo Done.
mpremote connect %MPREMOTE_PORT% fs ls :

endlocal