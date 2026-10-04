@echo off
setlocal
set ROOT=%~1
if "%ROOT%"=="" set ROOT=.
set SELF=%~dp0
for %%I in ("%SELF%..") do set ACR_ROOT=%%~fI
set NATIVE=%SELF%common\native\acr-toolbox\dist\acr-toolbox.exe
set PY_ANALYZE=%SELF%common\small\analyze-and-recommend\script\analyze_and_recommend.py
set PY_LANG=%SELF%common\small\language-environment-plan\script\language_environment_plan.py
set PY_LANG_SETUP=%SELF%common\small\language-setup\script\language_setup.py
set PY_LANG_RUN=%SELF%common\small\language-run\script\language_run.py

echo [ai-context-reducer] environment
if exist "%NATIVE%" (
  "%NATIVE%" env
  if errorlevel 1 goto failed
  echo [ai-context-reducer] language environments
  "%NATIVE%" language-env
  if errorlevel 1 goto failed
  echo [ai-context-reducer] project analysis
  "%NATIVE%" analyze "%ROOT%"
  if errorlevel 1 goto failed
  echo [ai-context-reducer] language tool plan
  "%NATIVE%" language-setup "%ROOT%"
  if errorlevel 1 goto failed
  echo [ai-context-reducer] shallow language analysis
  "%NATIVE%" language-run "%ROOT%"
  if errorlevel 1 goto failed
  goto done
)

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%PY_LANG%"
  if errorlevel 1 goto failed
  py -3 "%PY_ANALYZE%" "%ROOT%"
  if errorlevel 1 goto failed
  py -3 "%PY_LANG_SETUP%" "%ROOT%"
  if errorlevel 1 goto failed
  py -3 "%PY_LANG_RUN%" --acr-root "%ACR_ROOT%" "%ROOT%"
  if errorlevel 1 goto failed
  goto done
)

where python >nul 2>nul
if %errorlevel%==0 (
  python "%PY_LANG%"
  if errorlevel 1 goto failed
  python "%PY_ANALYZE%" "%ROOT%"
  if errorlevel 1 goto failed
  python "%PY_LANG_SETUP%" "%ROOT%"
  if errorlevel 1 goto failed
  python "%PY_LANG_RUN%" --acr-root "%ACR_ROOT%" "%ROOT%"
  if errorlevel 1 goto failed
  goto done
)

echo No native acr-toolbox or Python runtime found. 1>&2
echo Use a prebuilt acr-toolbox.exe for this architecture. 1>&2
endlocal & exit /b 2

:done
echo [ai-context-reducer] setup policy: run only shallow compatible language analysis automatically; do not install missing runtimes or run Medium/Large analyzers automatically.
endlocal & exit /b 0

:failed
set "SETUP_EXIT_CODE=%errorlevel%"
if "%SETUP_EXIT_CODE%"=="0" set "SETUP_EXIT_CODE=1"
echo [ai-context-reducer] setup failed with exit code %SETUP_EXIT_CODE%. 1>&2
endlocal & exit /b %SETUP_EXIT_CODE%
