@echo off
setlocal enabledelayedexpansion

set MPREMOTE_PORT=auto
set error_count=0

echo Deploying files from src to ESP32 ^(excluding files starting with "_"^)...

REM Copy top-level files
for %%F in (src\*) do (
    if not exist "%%F\" (
        set "filename=%%~nxF"
        if not "!filename:~0,1!"=="_" (
            echo Copying !filename!...
            mpremote connect %MPREMOTE_PORT% fs cp "%%F" :
            if errorlevel 1 set /a error_count+=1
        ) else (
            echo Skipping !filename! ^(starts with "_"^)
        )
    )
)

REM Copy top-level directories recursively
for /d %%D in (src\*) do (
    set "dirname=%%~nxD"
    if not "!dirname:~0,1!"=="_" (
        echo Copying directory !dirname!\...
        mpremote connect %MPREMOTE_PORT% fs cp -r "%%D" :
        if errorlevel 1 set /a error_count+=1
    ) else (
        echo Skipping !dirname! directory ^(starts with "_"^)
    )
)

echo.
if !error_count! equ 0 (
    echo Deployment successful.
) else (
    echo Deployment completed with !error_count! error^(s^).
    exit /b 1
)

endlocal