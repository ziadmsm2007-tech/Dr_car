@echo off
chcp 65001 >nul
title DrCar - دكتور عربيتك
echo ========================================
echo   🚗 DrCar شغال...
echo   افتح المتصفح على: http://127.0.0.1:5000
echo ========================================
echo.
python app.py
if errorlevel 1 (
  echo.
  echo جرب: py app.py
  py app.py
)
pause
