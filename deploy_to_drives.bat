@echo off
echo ===== Solar Assistant Deployment Script =====
echo This script will copy the Solar Assistant application to multiple drives.
echo Target drives: D:, G:, H:, I:
echo.

set SOURCE_DIR=%~dp0
set DEST_FOLDER=solar_assistant

echo Source directory: %SOURCE_DIR%
echo.

REM Check if PyInstaller has been run
if not exist "%SOURCE_DIR%dist\app.exe" (
    echo ERROR: Executable not found at %SOURCE_DIR%dist\app.exe
    echo Please run PyInstaller first with the following command:
    echo.
    echo pyinstaller --onefile --noconfirm --add-data "templates;templates" --add-data "static;static" --add-data "prompts;prompts" --add-data "config.py;." app.py
    echo.
    goto :EOF
)

echo Creating deployment package...
echo.

REM Check and deploy to D: drive
if exist D:\ (
    echo Deploying to D: drive...
    if not exist "D:\%DEST_FOLDER%" mkdir "D:\%DEST_FOLDER%"
    xcopy "%SOURCE_DIR%dist\app.exe" "D:\%DEST_FOLDER%\" /Y
    echo @echo off > "D:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo echo Starting Solar Assistant... >> "D:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo app.exe --port 8003 >> "D:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo echo When finished, close this window. >> "D:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo Deployment to D: drive complete.
) else (
    echo D: drive not found, skipping.
)
echo.

REM Check and deploy to G: drive
if exist G:\ (
    echo Deploying to G: drive...
    if not exist "G:\%DEST_FOLDER%" mkdir "G:\%DEST_FOLDER%"
    xcopy "%SOURCE_DIR%dist\app.exe" "G:\%DEST_FOLDER%\" /Y
    echo @echo off > "G:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo echo Starting Solar Assistant... >> "G:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo app.exe --port 8003 >> "G:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo echo When finished, close this window. >> "G:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo Deployment to G: drive complete.
) else (
    echo G: drive not found, skipping.
)
echo.

REM Check and deploy to H: drive
if exist H:\ (
    echo Deploying to H: drive...
    if not exist "H:\%DEST_FOLDER%" mkdir "H:\%DEST_FOLDER%"
    xcopy "%SOURCE_DIR%dist\app.exe" "H:\%DEST_FOLDER%\" /Y
    echo @echo off > "H:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo echo Starting Solar Assistant... >> "H:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo app.exe --port 8003 >> "H:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo echo When finished, close this window. >> "H:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo Deployment to H: drive complete.
) else (
    echo H: drive not found, skipping.
)
echo.

REM Check and deploy to I: drive
if exist I:\ (
    echo Deploying to I: drive...
    if not exist "I:\%DEST_FOLDER%" mkdir "I:\%DEST_FOLDER%"
    xcopy "%SOURCE_DIR%dist\app.exe" "I:\%DEST_FOLDER%\" /Y
    echo @echo off > "I:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo echo Starting Solar Assistant... >> "I:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo app.exe --port 8003 >> "I:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo echo When finished, close this window. >> "I:\%DEST_FOLDER%\run_solar_assistant.bat"
    echo Deployment to I: drive complete.
) else (
    echo I: drive not found, skipping.
)
echo.

echo ===== Deployment Summary =====
echo.
if exist "D:\%DEST_FOLDER%\app.exe" echo Solar Assistant deployed to D:\%DEST_FOLDER%
if exist "G:\%DEST_FOLDER%\app.exe" echo Solar Assistant deployed to G:\%DEST_FOLDER%
if exist "H:\%DEST_FOLDER%\app.exe" echo Solar Assistant deployed to H:\%DEST_FOLDER%
if exist "I:\%DEST_FOLDER%\app.exe" echo Solar Assistant deployed to I:\%DEST_FOLDER%
echo.
echo To run the application on any computer, navigate to the solar_assistant folder
echo on the drive and double-click run_solar_assistant.bat.
echo Then open a web browser and go to http://localhost:8003
echo.
echo Press any key to exit...
pause > nul