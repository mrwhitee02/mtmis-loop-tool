@echo off
title MTMIS Bridge - band nahi karna
cd /d "%~dp0"
echo.
echo  ============================================
echo   MTMIS Bridge chal raha hai
echo   Is window ko band NA karo jab tak tool use kar rahe ho.
echo   Tool page: https://zinko.free.nf/mtmis-loop-tool.html
echo  ============================================
echo.
python mtmis-bridge.py
if %errorlevel% neq 0 (
  echo.
  echo  'python' se nahi chala - 'py' se try kar raha hun...
  echo.
  py mtmis-bridge.py
)
echo.
echo  Bridge band ho gaya. Dobara chalane ke liye is file ko dobara double-click karo.
pause
