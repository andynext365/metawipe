@echo off
title office metadata cleaner
chcp 65001
set "RUNPY=C:\Users\Administrator\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
set "SRCPY=C:\Users\Administrator\WorkBuddy\2026-11-11-11-12-57\tools\docx_metadata_cleaner.py"
echo ================================================
echo  Drag and drop .docx / .pptx / .xlsx / .pdf
echo  Output: same folder, cleaned copy
echo ================================================
if not exist "%SRCPY%" (
  echo [ERROR] Source script not found: %SRCPY%
  echo Do not move or rename the WorkBuddy workspace folder.
  pause
  exit /b 1
)
"%RUNPY%" -X utf8 "%SRCPY%" --noinput %*
echo.
echo All done. Press any key to exit...
pause
