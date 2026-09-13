@echo off
setlocal
cd /d %~dp0
if not exist dist mkdir dist
go test ./...
if errorlevel 1 exit /b 1
go build -trimpath -ldflags="-s -w" -o dist\go-symbols.exe .
if errorlevel 1 exit /b 1
echo built: %cd%\dist\go-symbols.exe
