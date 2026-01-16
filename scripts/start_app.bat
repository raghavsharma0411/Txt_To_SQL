@echo off
echo Starting Text-to-SQL Generator...
echo.

REM Check if we're in the right directory
if not exist "src\app.py" (
    echo Error: src\app.py not found!
    echo Please run this script from the project root directory.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found!
    echo Please configure your API keys in the .env file.
    echo.
)

REM Start the application
echo Starting Streamlit application...
python -m streamlit run src\app.py

pause