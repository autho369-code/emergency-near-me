@echo off
cd /d "C:\Users\autho\emergency-near-me"
start http://localhost:8080/agent_dashboard.html
start http://localhost:8080/dashboard.html
python -m http.server 8080
