@echo off
cd /d "%~dp0"
py -3 scripts\serve_library.py --open
if errorlevel 1 pause
