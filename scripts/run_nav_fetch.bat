@echo off
echo ---- %date% %time% ---- >> "C:\Projects\cp_project\logs\nav_fetch.log"
"C:\Program Files\Python314\python.exe" "C:\Projects\cp_project\scripts\live_nav_fetch.py" >> "C:\Projects\cp_project\logs\nav_fetch.log" 2>&1
