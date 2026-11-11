@echo off
title office pdf metadata cleaner
chcp 65001
set "TOOLDIR=%~dp0"
echo ================================================
echo  Drag and drop .docx / .pptx / .xlsx / .pdf
echo  Output: same folder, cleaned copy
echo ================================================
"C:\Users\Administrator\.workbuddy\binaries\python\envs\default\Scripts\python.exe" -X utf8 "%TOOLDIR%docx_metadata_cleaner.py" --noinput %*
echo.
echo All done. Press any key to exit...
pause
