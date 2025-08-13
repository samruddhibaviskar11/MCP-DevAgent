@echo off
echo 🚀 Starting MCP Agent - AI Git Assistant...
echo 📂 Project Directory: %CD%

REM Parse args: start.bat [fast|full] [port] [preload]
set MODE=%1
if "%MODE%"=="" set MODE=full
set PORT=%2
if "%PORT%"=="" set PORT=8501
set PRELOAD=%3

if /I "%MODE%"=="fast" (
	set FAST_MODE=1
	set MODE_NAME=FAST
) else (
	set FAST_MODE=0
	set MODE_NAME=FULL
)

echo ⚙️ Mode: %MODE_NAME%   Port: %PORT%
if /I "%PRELOAD%"=="preload" echo 📥 Preloading models enabled

echo.
REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
	echo ❌ Virtual environment not found!
	echo 🔧 Creating virtual environment...
	python -m venv .venv
	if errorlevel 1 (
		echo ❌ Failed to create virtual environment
		pause
		exit /b 1
	)
	
	echo 📦 Installing dependencies...
	.venv\Scripts\python.exe -m pip install --disable-pip-version-check -r requirements.txt
	if errorlevel 1 (
		echo ❌ Failed to install dependencies
		pause
		exit /b 1
	)
) else (
	echo ✅ Virtual environment found
)

REM Optional: preload models to warm cache
if /I "%PRELOAD%"=="preload" (
	echo 📥 Preloading models (one-time warmup)...
	.venv\Scripts\python.exe preload_models.py
)

echo 🤖 Starting Streamlit application...
echo 🌐 Application will open at: http://localhost:%PORT%
echo 🛑 Press Ctrl+C to stop the application
echo.

REM Run the app with selected mode and port
set FAST_MODE=%FAST_MODE%
.venv\Scripts\python.exe -m streamlit run app.py --server.port=%PORT% --server.headless=true

echo.
echo 👋 Application stopped. Press any key to exit...
pause >nul 