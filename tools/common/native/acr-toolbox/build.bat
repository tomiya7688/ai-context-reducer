@echo off
setlocal
cd /d %~dp0
go test ./...
if errorlevel 1 exit /b 1
if not exist ..\..\..\..\bin mkdir ..\..\..\..\bin
if "%GOOS%"=="" for /f %%i in ('go env GOOS') do set GOOS=%%i
if "%GOARCH%"=="" for /f %%i in ('go env GOARCH') do set GOARCH=%%i
set OUT=..\..\..\..\bin\acr-toolbox
if /I "%GOOS%"=="windows" set OUT=%OUT%.exe
set CGO_ENABLED=0
go build -trimpath -ldflags="-s -w" -o "%OUT%" .
if errorlevel 1 exit /b 1
echo built %OUT% (%GOOS%/%GOARCH%)
