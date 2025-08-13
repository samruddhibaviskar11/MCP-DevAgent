"""
Configuration settings for MCP Agent
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

# AI Chat Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
USE_AI_SERVICE = os.getenv('USE_AI_SERVICE', 'false').lower() == 'true'
AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')  # or 'claude-3-sonnet'

# Chat Response Configuration
MAX_RESPONSE_LENGTH = 2000
MAX_CONTEXT_FILES = 20
ENABLE_CODE_SUGGESTIONS = True
ENABLE_SMART_SEARCH = True

# File Processing Limits
MAX_FILE_SIZE = 50000  # 50KB
MAX_FILES_DISPLAY = 50

# Repository Analysis Settings
IGNORE_DIRS = ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build']
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