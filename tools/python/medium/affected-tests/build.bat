@echo off
setlocal
cd /d %~dp0
if not exist dist mkdir dist
set PYBIN=python
where py >nul 2>nul && set PYBIN=py -3
%PYBIN% -m zipapp . -m "affected_tests:main" -o dist\affected-tests.pyz -p "/usr/bin/env python3"
if errorlevel 1 exit /b 1
echo built: %cd%\dist\affected-tests.pyz
