@echo off
REM Windows batch file to run job analysis

if "%1"=="" (
    echo Usage: analyze-job.bat [job_posting_file]
    echo Example: analyze-job.bat paste.txt
    exit /b 1
)

echo Starting job analysis...
python 01-job-description-analysis.py %*

pause 