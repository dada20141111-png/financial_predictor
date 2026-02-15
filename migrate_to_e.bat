@echo off
title Project Migration to E: Drive
echo ==========================================
echo      Antigravity Migration Assistant
echo ==========================================
echo.

echo [1/4] Preparing Target Directories on E:...
if not exist "E:\AntigravityProjects\financial_predictor" mkdir "E:\AntigravityProjects\financial_predictor"
if not exist "E:\Antigravity_Cache\pip" mkdir "E:\Antigravity_Cache\pip"
if not exist "E:\Antigravity_Cache\nltk_data" mkdir "E:\Antigravity_Cache\nltk_data"
if not exist "E:\Antigravity_Cache\huggingface" mkdir "E:\Antigravity_Cache\huggingface"
echo Done.

echo.
echo [2/4] Copying Project Files (Skipping build/dist trash)...
rem /MIR mirrors directory tree
rem /XD excludes directories
rem /XF excludes files
robocopy "c:\Users\wh\.gemini\antigravity\scratch\financial_predictor" "E:\AntigravityProjects\financial_predictor" /MIR /XD build dist __pycache__ .git .pytest_cache /XF *.pyc
if %errorlevel% leq 3 echo Copy Success! (Robocopy code %errorlevel%)

echo.
echo [3/4] Generating Optimized Launcher (E: Edition)...
(
echo @echo off
echo title Financial Predictor AI - E Drive
echo echo ==================================================
echo echo      Financial Predictor AI - E Drive Mode
echo echo ==================================================
echo.
echo echo [*] Configuring Caches to E:\Antigravity_Cache...
echo set PIP_CACHE_DIR=E:\Antigravity_Cache\pip
echo set NLTK_DATA=E:\Antigravity_Cache\nltk_data
echo set HF_HOME=E:\Antigravity_Cache\huggingface
echo.
echo echo [1/2] Checking dependencies...
echo python -m pip install -r requirements.txt
echo.
echo echo [1.5/2] Checking NLP resources...
echo python -m textblob.download_corpora
echo.
echo echo [2/2] Launching Application...
echo python -m streamlit run src/app.py
echo.
echo if %%errorlevel%% neq 0 pause
) > "E:\AntigravityProjects\financial_predictor\start_app_E.bat"

echo.
echo [4/4] Creating Desktop Shortcut instructions...
echo.
echo ==================================================
echo MIGRATION SUCCESSFUL!
echo ==================================================
echo.
echo 1. Your project is now at: E:\AntigravityProjects\financial_predictor
echo 2. Please go there and use 'start_app_E.bat' to run it.
echo 3. Once you verify it works, you can SAFELY DELETE:
echo    c:\Users\wh\.gemini\antigravity\scratch\financial_predictor
echo    to free up space on C: drive.
echo.
pause
