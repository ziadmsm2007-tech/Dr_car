@echo off
chcp 65001 >nul
title DrCar (HTTPS)
echo ========================================
echo   DrCar - HTTPS mode (GPS works on phone)
echo   Open: https://localhost:5000
echo   Browser warning about certificate: Advanced ^> Continue
echo ========================================
pip install cryptography -q
set USE_HTTPS=1
python app.py
if errorlevel 1 py app.py
pause
