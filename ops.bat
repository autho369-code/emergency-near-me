@echo off
cd /d "C:\Users\autho\emergency-near-me"

:menu
cls
echo.
echo   EMERGENCY NEAR ME — Operations System
echo   ======================================
echo.
echo   1  Open Dashboard (view all 4,545 slots)
echo   2  Start Local Server (browser-based, http://localhost:8080)
echo   3  Edit Provider Database (providers.json)
echo   4  View Outreach Emails (drafted by agent)
echo   5  Open GitHub Repo
echo   6  Git Pull (sync latest changes)
echo   0  Exit
echo.
set /p choice="Enter option: "

if "%choice%"=="1" start "" "dashboard.html"
if "%choice%"=="2" start http://localhost:8080 & python -m http.server 8080
if "%choice%"=="3" start notepad "providers.json"
if "%choice%"=="4" if exist "outreach_emails.txt" (start notepad "outreach_emails.txt") else (echo No emails yet. Agent runs Wednesdays. & pause)
if "%choice%"=="5" start https://github.com/autho369-code/emergency-near-me
if "%choice%"=="6" git pull & pause
if "%choice%"=="0" goto :eof

goto menu
