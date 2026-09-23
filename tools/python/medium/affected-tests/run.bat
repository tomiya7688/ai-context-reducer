@echo off
setlocal
cd /d %~dp0
set PYBIN=python
where py >nul 2>nul && set PYBIN=py -3
%PYBIN% script\affected_tests.py %*
