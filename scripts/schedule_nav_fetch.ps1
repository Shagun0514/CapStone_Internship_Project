<#
Bluestock MF — B1: Schedule live NAV fetch
--------------------------------------------
Registers a Windows Task Scheduler job that runs scripts\live_nav_fetch.py
every weekday (Mon-Fri) at 8:00 PM.

USAGE (run once, from an elevated/admin PowerShell, from the project root):
    .\scripts\schedule_nav_fetch.ps1

To remove the scheduled task later:
    Unregister-ScheduledTask -TaskName "Bluestock_NAV_Fetch" -Confirm:$false
#>

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ScriptPath  = Join-Path $ProjectRoot "scripts\live_nav_fetch.py"
$PythonExe   = (Get-Command python).Source
$LogDir      = Join-Path $ProjectRoot "logs"

if (-not (Test-Path $ScriptPath)) {
    throw "Could not find live_nav_fetch.py at $ScriptPath. Run this script from the project root."
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogFile = Join-Path $LogDir "nav_fetch.log"

# Wrap the python call so stdout/stderr get logged with a timestamp
$WrapperPath = Join-Path $ProjectRoot "scripts\run_nav_fetch.bat"
@"
@echo off
echo ---- %date% %time% ---- >> "$LogFile"
"$PythonExe" "$ScriptPath" >> "$LogFile" 2>&1
"@ | Set-Content -Path $WrapperPath -Encoding ASCII

$Action  = New-ScheduledTaskAction -Execute $WrapperPath
$Trigger = New-ScheduledTaskTrigger -Weekly `
    -DaysOfWeek Monday, Tuesday, Wednesday, Thursday, Friday `
    -At "20:00"
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd

Register-ScheduledTask `
    -TaskName "Bluestock_NAV_Fetch" `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Fetches live NAV data from mfapi.in for all Bluestock MF schemes every weekday at 8 PM." `
    -Force

Write-Host "Scheduled task 'Bluestock_NAV_Fetch' created."
Write-Host "Runs every weekday (Mon-Fri) at 8:00 PM."
Write-Host "Logs will be written to: $LogFile"
Write-Host ""
Write-Host "Verify it in Task Scheduler (taskschd.msc) or run:"
Write-Host "    Get-ScheduledTask -TaskName Bluestock_NAV_Fetch"
