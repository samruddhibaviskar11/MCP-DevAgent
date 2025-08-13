# 🚀 Setup Guide for Office Laptops

This guide helps you set up MCP Agent on office laptops with limited permissions using a local virtual environment.

## ✅ What We've Set Up For You

### 🎯 **Problem Solved: No Admin Rights Needed**
- ✅ Local virtual environment in `.venv/`
- ✅ All dependencies cached locally
- ✅ Persistent across sessions
- ✅ No global Python package installation required

## 📁 Project Structure

```
MVP_Mcp_devagent/
├── .venv/                   # Virtual environment (DO NOT DELETE)
├── app.py                   # Main application
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── start.bat               # Windows startup script
├── start.sh                # Linux/Mac startup script
├── preload_models.py       # Offline model caching
├── env.example             # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
```

## 🚀 Quick Start

### Option 1: Double-Click (Windows)
```
Double-click: start.bat
```

### Option 2: Command Line (Windows)
```cmd
start.bat
```

### Option 3: Command Line (Linux/Mac)
```bash
chmod +x start.sh
./start.sh
```

### Option 4: Manual (All Platforms)
```bash
.venv\Scripts\python.exe -m streamlit run app.py    # Windows
.venv/bin/python -m streamlit run app.py            # Linux/Mac
```

## 🌐 Accessing the Application

1. **Application starts automatically** at: http://localhost:8501
2. **Open your browser** and navigate to that URL
3. **Test the improved chat system**:
   - Load a repository in the "Repository" tab
   - Try the new intelligent chat in the "Chat" tab

## 🔧 Configuration (Optional)

### 1. GitHub Token Setup
```bash
# Copy the template
copy env.example .env          # Windows
cp env.example .env           # Linux/Mac

# Edit .env file and add your GitHub token
GITHUB_TOKEN=your_actual_token_here
```

**Get a GitHub token**: https://github.com/settings/tokens
- Permissions needed: `repo`, `read:org`, `read:user`

### 2. Offline Model Caching (For Blocked Internet)
```bash
# Run when you have internet access
.venv\Scripts\python.exe preload_models.py    # Windows
.venv/bin/python preload_models.py           # Linux/Mac
```

## 🎯 Testing the Improved Chat

1. **Clone a repository**:
   - Repository tab → Enter: `https://github.com/microsoft/vscode`
   - Click "Clone & Analyze Repository"

2. **Test intelligent responses**:
   ```
   "What's the structure of this project?"
   "Review the code quality"
   "Suggest improvements"
   "What are the main files?"
   "What dependencies does this use?"
   ```

3. **Before vs After**:
   - **Before**: "No specific suggestions for this query."
   - **After**: Rich, contextual analysis with actionable insights!

## 🛠️ Troubleshooting

### Issue: Virtual Environment Missing
```bash
# Recreate it
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Issue: Streamlit Command Not Found
- ✅ **Use the provided scripts** (`start.bat` or `start.sh`)
- ✅ **Don't use global `streamlit` command**

### Issue: Permission Denied
- ✅ **Everything runs in user space** - no admin rights needed
- ✅ **Virtual environment is local** to your project folder

### Issue: Internet Blocked
```bash
# Pre-cache models when you have internet
.venv\Scripts\python.exe preload_models.py
```

## 🔒 Security for Office Environment

- ✅ **No global installations**
- ✅ **All data stays local**
- ✅ **No external API calls** (unless you configure GitHub token)
- ✅ **Secrets in `.env`** (not committed to git)
- ✅ **Virtual environment isolated**

## 📋 Daily Usage

### First Time Setup (Done!)
1. ✅ Virtual environment created
2. ✅ Dependencies installed
3. ✅ Scripts configured

### Every Day After
1. **Run**: `start.bat` (Windows) or `./start.sh` (Linux/Mac)
2. **Open**: http://localhost:8501
3. **Use**: Improved AI chat system!

## 💡 Pro Tips

1. **Bookmark** http://localhost:8501 in your browser
2. **Keep** the terminal window open while using the app
3. **Press Ctrl+C** in terminal to stop the application
4. **The `.venv` folder** contains everything - don't delete it!

## 🎉 What's New in Chat

- **🎯 Smart Query Classification**: Understands what you're asking
- **🧠 Context-Aware Responses**: Uses actual repository data
- **📊 Structured Output**: Professional formatting with insights
- **🔍 Repository-Specific**: Tailored advice for your project
- **💡 Actionable Suggestions**: Real improvements, not generic tips

**The chat now provides genuine value instead of "No specific suggestions for this query"!** 