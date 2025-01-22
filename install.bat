@echo off
:: Create virtual environment
python -m venv venv

:: Check if venv creation was successful
if errorlevel 1 (
    echo Failed to create virtual environment.
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate

:: Check if activation was successful
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

:: Install dependencies
pip install -r requirements.txt

:: Check if dependencies were installed successfully
if errorlevel 1 (
    echo Failed to install dependencies.
    exit /b 1
)

:: Setup complete
echo Installation complete!
pause
