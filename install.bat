@echo off
REM Kinda installation script for Windows - because Windows users deserve chaos too

echo 🤷 Installing kinda... (this might work on Windows)
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Python not found. Install Python 3.8+ first.
        echo 🤷 Try: https://python.org/downloads
        pause
        exit /b 1
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

echo ✅ Found Python (good enough)

REM Install kinda
echo 📦 Installing kinda-lang via pip...
%PYTHON_CMD% -m pip install -e .
if %errorlevel% neq 0 (
    echo 💥 Installation failed. Classic.
    echo 🤷 Try running as administrator or:
    echo    %PYTHON_CMD% -m pip install --user -e .
    pause
    exit /b 1
)

echo.
echo 🎉 Installation complete! (probably)
echo.
echo Try these commands:
echo   kinda --help      # See snarky help
echo   kinda examples    # View examples  
echo   kinda syntax      # Syntax reference
echo.
echo 🎲 Welcome to the chaos!
pause