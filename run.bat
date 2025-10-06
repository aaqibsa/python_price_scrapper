@echo off
REM Python Scrapper - Windows Run Script

echo Python Scrapper
echo ================

if "%1"=="" (
    echo Usage: run.bat [command]
    echo.
    echo Commands:
    echo   url-manager    Start the web interface
    echo   scraper        Run the price scraper
    echo   test-twilio    Test SMS functionality
    echo   setup          Run setup script
    echo   config-check   Check configuration
    echo.
    pause
    exit /b 1
)

if "%1"=="setup" (
    echo Running setup...
    python setup.py
    pause
    exit /b 0
)

if "%1"=="config-check" (
    echo Checking configuration...
    python main.py --config-check
    pause
    exit /b 0
)

if "%1"=="url-manager" (
    echo Starting URL Manager...
    python main.py url-manager
    pause
    exit /b 0
)

if "%1"=="scraper" (
    echo Starting Price Scraper...
    python main.py scraper
    pause
    exit /b 0
)

if "%1"=="test-twilio" (
    echo Testing Twilio...
    python main.py test-twilio
    pause
    exit /b 0
)

echo Unknown command: %1
echo.
echo Available commands:
echo   url-manager    Start the web interface
echo   scraper        Run the price scraper
echo   test-twilio    Test SMS functionality
echo   setup          Run setup script
echo   config-check   Check configuration
echo.
pause
