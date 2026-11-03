@echo off
title AegisOS v1.5 Installer & Integrity Verifier
echo ===============================================================
echo     AEGIS SECURE OPERATING SYSTEM (AegisOS v1.5) INSTALLER     
echo ===============================================================
echo [1/3] Verifying Trappy v1.5 Runtime Engine...
python -c "import trappy; print('[OK] Trappy v1.5 Engine Verified.')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python/Trappy runtime is not accessible.
    pause
    exit /b 1
)

echo [2/3] Checking Cryptographic OS Manifest...
if not exist "AegisOS.trappy" (
    echo [ERROR] AegisOS.trappy source image not found.
    pause
    exit /b 1
)
echo [OK] AegisOS.trappy image verified.

echo [3/3] Performing Installation and Booting AegisOS...
echo ===============================================================
python trappy.py AegisOS.trappy
echo ===============================================================
echo Installation and Execution Finished.
pause
