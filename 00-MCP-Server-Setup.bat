@echo off
REM 00-MCP Server Setup Script (Batch)
REM This script provides options to run the MCP server setup in Python or PowerShell

echo.
echo 🚀 MCP Server Setup Script
echo ========================================
echo.
echo Choose your preferred method:
echo 1. Run Python script (00-MCP-Server-Setup.py)
echo 2. Run PowerShell script (00-MCP-Server-Setup.ps1)
echo 3. Run PowerShell script in DRY RUN mode
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto python
if "%choice%"=="2" goto powershell
if "%choice%"=="3" goto dryrun
if "%choice%"=="4" goto exit
goto invalid

:python
echo.
echo 🐍 Running Python setup script...
echo.
python 00-MCP-Server-Setup.py
goto end

:powershell
echo.
echo 💻 Running PowerShell setup script...
echo.
powershell -ExecutionPolicy Bypass -File "00-MCP-Server-Setup.ps1"
goto end

:dryrun
echo.
echo 🔍 Running PowerShell setup script in DRY RUN mode...
echo.
powershell -ExecutionPolicy Bypass -File "00-MCP-Server-Setup.ps1" -DryRun
goto end

:invalid
echo.
echo ❌ Invalid choice. Please enter 1, 2, 3, or 4.
echo.
pause
goto start

:exit
echo.
echo 👋 Goodbye!
goto end

:end
echo.
echo ========================================
echo.
pause 