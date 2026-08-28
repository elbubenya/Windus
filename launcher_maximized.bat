```bat
@echo off
cd /d "%~dp0"

start "" /MAX cmd /c "python main.py 2> "%TEMP%\windus_stderr.tmp""

set EXITCODE=%errorlevel%

if not %EXITCODE%==0 (
    echo [%date% %time%] Crashed with exit code %EXITCODE% >> crashlog.txt
    type "%TEMP%\windus_stderr.tmp" >> crashlog.txt
    echo. >> crashlog.txt
)

del "%TEMP%\windus_stderr.tmp" 2>nul
```
