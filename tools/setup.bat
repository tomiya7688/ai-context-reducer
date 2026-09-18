@echo off
setlocal
set ROOT=%~1
if "%ROOT%"=="" set ROOT=.
set SELF=%~dp0
set NATIVE=%SELF%common\native\acr-toolbox\dist\acr-toolbox.exe
set PY_ANALYZE=%SELF%common\small\analyze-and-recommend\script\analyze_and_recommend.py
set PY_LANG=%SELF%common\small\language-environment-plan\script\language_environment_plan.py
set PY_LANG_SETUP=%SELF%common\small\language-setup\script\language_setup.py

echo [ai-context-reducer] environment
if exist "%NATIVE%" (
  "%NATIVE%" env
  echo [ai-context-reducer] language environments
  "%NATIVE%" language-env
  echo [ai-context-reducer] project analysis
  "%NATIVE%" analyze "%ROOT%"
  echo [ai-context-reducer] language tool plan
  "%NATIVE%" language-setup "%ROOT%"
  goto done
)

where py >nul 2>nul
if %errorlevel%==0 (
  py "%PY_LANG%"
  py "%PY_ANALYZE%" "%ROOT%"
  py "%PY_LANG_SETUP%" "%ROOT%"
  goto done
)

where python >nul 2>nul
if %errorlevel%==0 (
  python "%PY_LANG%"
  python "%PY_ANALYZE%" "%ROOT%"
  python "%PY_LANG_SETUP%" "%ROOT%"
  goto done
)

echo No native acr-toolbox or Python runtime found. 1>&2
echo Use a prebuilt acr-toolbox.exe for this architecture. 1>&2
exit /b 2

:done
echo [ai-context-reducer] setup policy: enable only compatible language-specific tools; do not install missing runtimes automatically.
endlocal
