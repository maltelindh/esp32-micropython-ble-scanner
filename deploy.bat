@echo off
REM Deploy all files from src folder to ESP32 (excluding files starting with "_")
REM Change MPREMOTE_PORT to your COM port if auto-detection fails (e.g., COM5)
set MPREMOTE_PORT=auto

echo Deploying files from src to ESP32 (excluding files starting with "_")...

setlocal enabledelayedexpansion
set error_count=0

REM Copy individual files, skipping those starting with "_"
for %%F in (src\*) do (
    set filename=%%~nxF
    if not "!filename:~0,1!"=="_" (
        echo Copying !filename!...
        mpremote connect %MPREMOTE_PORT% fs cp %%F :
        if !errorlevel! neq 0 set /a error_count+=1
    ) else (
        echo Skipping !filename! (starts with "_")
    )
)

REM Copy subdirectories recursively, excluding directories starting with "_"
for /d %%D in (src\*) do (
    set dirname=%%~nxD
    if not "!dirname:~0,1!"=="_" (
        echo Copying directory !dirname!\...
        mpremote connect %MPREMOTE_PORT% fs cp %%D :
        if !errorlevel! neq 0 set /a error_count+=1
    ) else (
        echo Skipping !dirname! directory (starts with "_")
    )
)

echo.
if %error_count% equ 0 (
    echo Deployment successful! Run console.bat to verify.
) else (
    echo Deployment completed with %error_count% error(s).
    exit /b 1
)
