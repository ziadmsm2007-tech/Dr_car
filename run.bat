@echo off
title DrCar
echo.
echo   Starting DrCar on http://127.0.0.1:5000 ...
echo.
echo   Login with Google and Telegram are both ready.
echo   Press Ctrl+C to stop the server.
echo.
python app.py
if errorlevel 1 py app.py
pause
