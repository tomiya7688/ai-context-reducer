@echo off
setlocal
set ROOT=%~1
if "%ROOT%"=="" set ROOT=.
set BASE=%~dp0
if exist "%BASE%bin\acr-toolbox.exe" (
  "%BASE%bin\acr-toolbox.exe" analyze "%ROOT%"
  exit /b %errorlevel%
)
where python >nul 2>nul
if not errorlevel 1 (
  python "%BASE%common\small\analyze-and-recommend\script\analyze_and_recommend.py" "%ROOT%"
  exit /b %errorlevel%
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%BASE%common\small\analyze-and-recommend\script\analyze_and_recommend.py" "%ROOT%"
  exit /b %errorlevel%
)
echo No usable analyzer found. Download acr-toolbox.exe or install Python 3. 1>&2
exit /b 2
