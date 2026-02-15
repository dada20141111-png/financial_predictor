@echo off
title Financial Predictor AI - Launcher
echo ==================================================
echo       Financial Predictor AI - v1.0
echo ==================================================
echo.

echo [1/2] Checking and installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies! Please check your internet connection.
    pause
    exit /b
)

echo.
echo [2/2] Launching Application...
echo.
echo Please wait for the browser to open...
python -m streamlit run src/app.py

if %errorlevel% neq 0 (
    echo Application crashed! See error above.
    pause
)
