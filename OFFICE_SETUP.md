# 🏢 Office Environment Setup Guide

## 🎯 Optimized for Limited Permissions & Offline Usage

This guide helps you set up MCP Agent on office laptops with restricted permissions, proxy networks, and limited internet access.

## ✅ Prerequisites

- **Python 3.8+** installed (usually available on office machines)
- **No admin rights required** - everything runs in user space
- **Internet access** for initial setup (can work offline afterward)

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

**Windows:**
```cmd
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

1. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```

2. **Activate it:**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac  
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt --cache-dir .venv/pip-cache
   ```

4. **Create environment file:**
   ```bash
   cp env.example .env
   ```

## 🔧 Configuration

### 1. GitHub Token (Optional but Recommended)

Edit `.env` file:
```env
GITHUB_TOKEN=your_token_here
```

**Get token:** https://github.com/settings/tokens
- **Permissions needed:** `repo`, `read:org`, `read:user`
- **Benefits:** Access private repos, higher rate limits

### 2. Offline Model Caching

For restricted internet environments:
```bash
# Run when you have internet access
python preload_models.py
```

This downloads AI models locally for offline usage.

## 🏃‍♂️ Running the Application

### Quick Start Scripts

**Windows:**
```cmd
run_app.bat     # New optimized script
start.bat       # Original script
```

**Linux/Mac:**
```bash
./run_app.sh    # New optimized script  
./start.sh      # Original script
```

### Manual Start
```bash
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

streamlit run app.py
```

## 🌐 Access

- **Local:** http://localhost:8501
- **Network:** http://YOUR_IP:8501

## 🔒 Office Environment Benefits

### ✅ Security & Compliance
- **No admin rights needed** - runs entirely in user space
- **Local data storage** - no cloud dependencies
- **Isolated environment** - .venv contains everything
- **Secrets management** - .env file for tokens

### ✅ Network & Proxy Friendly
- **Pip caching** - faster installs on slow networks
- **Offline capable** - works without internet after setup
- **Proxy support** - Python handles corporate proxies
- **Local models** - AI features work offline

### ✅ Reproducible Setup
- **Version pinning** - consistent dependency versions
- **Cached dependencies** - reuse across team members
- **Automated scripts** - one-click setup
- **Cross-platform** - Windows, Linux, Mac support

## 🛠️ Troubleshooting

### Port 8501 Already in Use
```bash
# Windows
netstat -ano | findstr :8501
taskkill /pid PID_NUMBER /f

# Linux/Mac  
lsof -i :8501
kill -9 PID_NUMBER
```

### Python Not Found
```bash
# Check Python installation
python --version
python3 --version

# Add to PATH if needed (Windows)
set PATH=%PATH%;C:\Python39;C:\Python39\Scripts
```

### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf .venv       # Linux/Mac
rmdir /s .venv     # Windows

python -m venv .venv
```

### Proxy Issues
```bash
# Set proxy for pip
pip install --proxy http://proxy.company.com:8080 -r requirements.txt
```

### Permission Errors
```bash
# Ensure you're in user directory
cd %USERPROFILE%\Documents\MCP_Agent  # Windows
cd $HOME/MCP_Agent                    # Linux/Mac
```

## 📁 Directory Structure

```
MCP_Agent/
├── .venv/                 # Virtual environment (DO NOT DELETE)
│   ├── pip-cache/         # Cached packages for speed
│   └── ...
├── .env                   # Your secrets (not in git)
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── setup.bat/setup.sh     # One-time setup
├── run_app.bat/run_app.sh # Quick launch
└── preload_models.py      # Offline model caching
```

## 💡 Office Pro Tips

### 1. Team Sharing
```bash
# Share the setup (without .venv)
zip -r mcp-agent-setup.zip . -x ".venv/*" ".env"
```

### 2. Faster Installs
```bash
# Use existing team member's cache
cp -r teammate/.venv/pip-cache .venv/
```

### 3. Offline Usage
```bash
# Cache everything when online
python preload_models.py
pip download -r requirements.txt -d offline-packages/
```

### 4. Multiple Projects
```bash
# Each project gets its own .venv
mkdir project-a && cd project-a
python -m venv .venv
```

## 🎯 Performance Optimizations

### Fast Startup
- **Cached dependencies** in `.venv/pip-cache/`
- **Pre-downloaded models** via `preload_models.py`
- **Quick launch scripts** handle port conflicts

### Low Resource Usage
- **Lightweight models** for sentence transformers
- **Efficient caching** reduces memory usage
- **Minimal network calls** when offline

### Team Efficiency
- **Reproducible environments** across team
- **Automated setup** reduces onboarding time
- **Offline capability** works in restricted networks

## 🔍 Verification

Run these to verify your setup:

```bash
# Check Python packages
python -c "import streamlit; print('✅ Streamlit OK')"
python -c "import git; print('✅ GitPython OK')"
python -c "import github; print('✅ PyGithub OK')"

# Check application
curl http://localhost:8501
```

## 📞 Support

- **Setup issues:** Check `setup.bat/setup.sh` output
- **Runtime errors:** Check Streamlit logs in terminal
- **Network issues:** Verify proxy settings
- **Performance:** Try offline mode with cached models

---

## 🎉 You're Ready!

Your MCP Agent is now optimized for office environments with:
- ✅ No admin rights required
- ✅ Cached dependencies for speed  
- ✅ Offline AI model support
- ✅ Proxy-friendly networking
- ✅ Secure local data storage

**Start the app:** `run_app.bat` (Windows) or `./run_app.sh` (Linux/Mac)
**Access:** http://localhost:8501 