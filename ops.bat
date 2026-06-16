@echo off
cd /d "C:\Users\autho\emergency-near-me"
title EmergencyNearMe — Operations System

:menu
cls
echo.
echo   ╔══════════════════════════════════════════╗
echo   ║   EMERGENCY NEAR ME — Agent Command     ║
echo   ╚══════════════════════════════════════════╝
echo.
echo   ──────── VIEW ────────
echo   1  Open Dashboard (see all 22,725 vendor slots)
echo   2  Start Local Server (http://localhost:8080)
echo.
echo   ──────── AGENTS ────────
echo   3  RUN Research Agent (find 10 providers now)
echo   4  RUN Outreach Agent (draft emails for found providers)
echo   5  RUN Supervisor (pipeline health check)
echo.
echo   ──────── FILES ────────
echo   6  Edit providers.json (vendor database)
echo   7  View outreach_emails.txt (ready to send)
echo   8  View AGENT_COMMANDS.md (full reference)
echo.
echo   ──────── SYSTEM ────────
echo   9  Git Pull (sync latest changes from agents)
echo   0  Exit
echo.
echo   Auto-schedule: Research Mon | Outreach Wed | Supervisor Fri | Billing 1st
echo.
set /p choice="Enter command: "

if "%choice%"=="1" start http://localhost:8080/dashboard.html & python -m http.server 8080
if "%choice%"=="2" start http://localhost:8080 & python -m http.server 8080
if "%choice%"=="3" start "Research" cmd /c "hermes kanban create "Research: Find 10 providers (priority Illinois)" --assignee emn-research --body "Read providers.json. Find 10 searching slots in priority order: Illinois first, then neighboring states. Search 'emergency [service] [city]'. Fill vendor slots with real business name, phone, website. Change status to found. Git commit and push." & echo Task created. Check dashboard for results. & pause"
if "%choice%"=="4" start "Outreach" cmd /c "hermes kanban create "Outreach: Draft emails for found providers" --assignee emn-outreach --body "Read providers.json. Find vendors with status='found'. Draft outreach email for each. Save to outreach_emails.txt. Change status to contacted. Git commit and push." & echo Task created. Check outreach_emails.txt for drafts. & pause"
if "%choice%"=="5" start "Supervisor" cmd /c "hermes kanban create "Supervisor: Pipeline health check" --assignee emn-supervisor --body "Read providers.json. Check status counts. Flag any contacted providers older than 7 days. Report what Mirsad should do next. Keep under 200 words." & echo Task created. & pause"
if "%choice%"=="6" start notepad "providers.json"
if "%choice%"=="7" if exist "outreach_emails.txt" (start notepad "outreach_emails.txt") else (echo No emails yet. Run Outreach Agent first. & pause)
if "%choice%"=="8" start notepad "AGENT_COMMANDS.md"
if "%choice%"=="9" git pull & echo Synced. & pause
if "%choice%"=="0" goto :eof

goto menu
