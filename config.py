"""
Configuration settings for MCP Agent
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

# File Processing Limits
MAX_FILE_SIZE = 50000  # 50KB
MAX_FILES_DISPLAY = 50

# Repository Analysis Settings
IGNORE_DIRS = ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
IGNORE_FILES = ['.DS_Store', 'Thumbs.db']

# Key file patterns to identify
KEY_FILES = [
    'readme.md', 'requirements.txt', 'setup.py', 'pyproject.toml',
    'dockerfile', 'docker-compose.yml', 'main.py', 'app.py',
    'package.json', 'yarn.lock', 'poetry.lock'
]

# Supported file extensions for analysis
SUPPORTED_EXTENSIONS = [
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c',
    '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt',
    '.md', '.txt', '.yml', '.yaml', '.json', '.xml'
] 