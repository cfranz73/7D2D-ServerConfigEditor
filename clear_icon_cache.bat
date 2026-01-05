@echo off
echo ========================================
echo Clearing Windows Icon Cache
echo ========================================
echo.
echo This will refresh the taskbar icon display.
echo Close all running instances of the app first!
echo.
pause

echo.
echo Stopping Windows Explorer...
taskkill /f /im explorer.exe

echo.
echo Deleting icon cache files...
cd /d %userprofile%\AppData\Local\Microsoft\Windows\Explorer
attrib -h IconCache.db
del IconCache.db
attrib -h iconcache_*.db
del iconcache_*.db

echo.
echo Restarting Windows Explorer...
start explorer.exe

echo.
echo ========================================
echo Icon cache cleared successfully!
echo ========================================
echo.
echo Now try running 7D2D-ServerConfigEditor.exe again.
echo The taskbar icon should display correctly.
echo.
pause
