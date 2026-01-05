@echo off
REM Build script for 7D2D Server Config Editor
REM This creates a standalone Windows executable with all resources bundled

echo ========================================
echo Building 7D2D Server Config Editor
echo ========================================
echo.

REM Clean previous build
if exist "dist\7D2D-ServerConfigEditor.exe" (
    echo Cleaning previous build...
    del /Q "dist\7D2D-ServerConfigEditor.exe"
)

REM Run PyInstaller
echo.
echo Running PyInstaller...
python -m PyInstaller --onefile --windowed --name "7D2D-ServerConfigEditor" --icon="icon.ico" --add-data "icon.ico;." --add-data "Logos and Images;Logos and Images" 7d2d_server_config_editor.py

REM Check if build succeeded
if exist "dist\7D2D-ServerConfigEditor.exe" (
    echo.
    echo ========================================
    echo Build completed successfully!
    echo ========================================
    echo.
    echo Executable location: dist\7D2D-ServerConfigEditor.exe
    echo File size:
    dir "dist\7D2D-ServerConfigEditor.exe" | findstr "7D2D-ServerConfigEditor.exe"
    echo.
) else (
    echo.
    echo ========================================
    echo Build FAILED!
    echo ========================================
    echo.
    echo Check the error messages above.
)

pause
