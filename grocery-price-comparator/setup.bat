@echo off
REM 🛒 GROCERY PRICE COMPARATOR - QUICK START SCRIPT (Windows)
REM This script sets up and runs the entire application

echo.
echo 🛒 =========================================
echo    GROCERY PRICE COMPARATOR - QUICK START
echo =========================================
echo.

REM Check Python version
echo 📌 Checking Python version...
python --version
echo.

REM Install dependencies
echo 📦 Installing dependencies...
pip install -q -r requirements.txt
echo ✅ Dependencies installed
echo.

REM Create data directory
echo 📂 Checking data files...
if not exist "data" (
    mkdir data
    echo    Creating data directory...
)
echo ✅ Data directory ready
echo.

REM Show next steps
echo =========================================
echo ✅ Setup complete!
echo =========================================
echo.
echo 🚀 TO START THE APPLICATION:
echo.
echo    Terminal 1 - Start Backend API:
echo    ^> uvicorn backend.main:app --reload --port 8000
echo.
echo    Terminal 2 - Open Frontend:
echo    ^> cd frontend ^&^& python -m http.server 8001
echo.
echo    Then visit:
echo    • Frontend: http://localhost:8001
echo    • API Docs: http://localhost:8000/docs
echo.
echo =========================================
echo.
echo 📚 View README.md for complete documentation
echo.

pause
