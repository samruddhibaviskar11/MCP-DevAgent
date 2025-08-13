@echo off
setlocal EnableDelayedExpansion

REM 🚀 MCP Agent Setup Script for Windows Office Environments
REM Optimized for limited permissions and offline usage

echo 🚀 MCP Agent Setup - Windows Office Environment Edition
echo 📂 Working Directory: %CD%
python --version 2>nul || (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)
echo.

echo 📋 Checking Python installation...
python --version

REM Step 1: Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 📋 Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created in .venv\
) else (
    echo ✅ Virtual environment already exists
)

REM Step 2: Activate virtual environment and upgrade pip
echo 📋 Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated

REM Step 3: Upgrade pip
echo 📋 Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Step 4: Install dependencies with caching
echo 📋 Installing dependencies from requirements.txt...
if exist "requirements.txt" (
    REM Install with pip cache for faster subsequent installs
    python -m pip install -r requirements.txt --cache-dir .venv\pip-cache
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ requirements.txt not found
    pause
    exit /b 1
)

REM Step 5: Create .env file if it doesn't exist
if not exist ".env" (
    if exist "env.example" (
        echo 📋 Creating .env file from template...
        copy env.example .env >nul
        echo ✅ .env file created from env.example
        echo ⚠️  Please edit .env file to add your GitHub token and API keys
    ) else (
        echo ⚠️  No env.example found, skipping .env creation
    )
) else (
    echo ✅ .env file already exists
)

REM Step 6: Preload models for offline usage (optional)
set /p "preload=🤖 Do you want to preload AI models for offline usage? (y/N): "
if /i "%preload%"=="y" (
    echo 📋 Preloading sentence transformer models...
    if exist "preload_models.py" (
        python preload_models.py
        echo ✅ Models preloaded for offline usage
    ) else (
        echo ⚠️  preload_models.py not found, skipping model preload
    )
)

REM Step 7: Create quick run script
echo 📋 Creating quick run script...
(
echo @echo off
echo echo 🚀 Starting MCP Agent...
echo.
echo REM Activate virtual environment
echo call .venv\Scripts\activate.bat
echo.
echo REM Check if port 8501 is in use and kill if necessary
echo netstat -ano ^| findstr :8501 ^>nul
echo if not errorlevel 1 ^(
echo     echo ⚠️  Port 8501 is already in use
echo     echo 🔄 Attempting to free port...
echo     for /f "tokens=5" %%%%a in ^('netstat -ano ^| findstr :8501'^) do taskkill /pid %%%%a /f ^>nul 2^>^&1
echo     timeout /t 2 /nobreak ^>nul
echo ^)
echo.
echo REM Start the application
echo echo 🌐 Starting Streamlit on http://localhost:8501
echo python -m streamlit run app.py --server.port=8501 --server.headless=true
echo.
echo echo 👋 Application stopped
echo pause
) > run_app.bat

echo ✅ Quick run script created: run_app.bat

REM Step 8: Display usage instructions
echo.
echo 🎉 Setup Complete!
echo.
echo 📋 Next Steps:
echo 1. Edit .env file with your GitHub token (optional but recommended)
echo 2. Run the application using one of these methods:
echo    • Quick start: run_app.bat
echo    • Manual: .venv\Scripts\activate ^&^& streamlit run app.py
echo    • Original: start.bat
echo.
echo 🌐 Application will be available at: http://localhost:8501
echo.
echo 🔧 Troubleshooting:
echo • If port 8501 is busy: netstat -ano ^| findstr :8501
echo • For permission issues: Run as regular user (admin not needed)
echo • For Python issues: Check python --version
echo.
echo 💡 Pro Tips for Office Environment:
echo • All dependencies are cached in .venv\pip-cache\
echo • Models are cached in %USERPROFILE%\.cache\torch\sentence_transformers\
echo • No admin rights required - everything runs in user space
echo • .env file keeps your secrets safe and local
echo.

REM Final verification
echo 📋 Verifying installation...
python -c "import streamlit; print(f'Streamlit {streamlit.__version__} installed')" 2>nul || echo ⚠️  Streamlit verification failed
python -c "import git; print('GitPython available')" 2>nul || echo ⚠️  GitPython verification failed
python -c "import github; print('PyGithub available')" 2>nul || echo ⚠️  PyGithub verification failed

echo ✅ 🎯 MCP Agent is ready to use!
echo.
echo Press any key to exit setup...
pause >nul 