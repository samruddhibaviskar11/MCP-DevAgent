# 🤖 MCP Agent - AI Git Assistant

An open-source AI-powered developer assistant that helps analyze GitHub repositories, understand issues, and provide code suggestions.

## ✨ Features

- **📂 Repository Cloning**: Clone and analyze GitHub repositories
- **🔍 Structure Analysis**: Understand codebase structure and file organization
- **🐛 GitHub Issues Integration**: Fetch and analyze open issues
- **💬 AI Chat Interface**: Natural language interaction with repository content
- **⚡ Code Suggestions**: Pattern-based code recommendations

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

### 3. Open in Browser

The app will open at `http://localhost:8501`

## 🔧 Usage

### Basic Setup
1. **Repository Tab**: Enter a GitHub repository URL and click "Clone & Analyze Repository"
2. **Issues Tab**: Fetch open issues from the repository (GitHub token optional)
3. **Analysis Tab**: Browse repository files and view their content
4. **Chat Tab**: Ask questions about the repository and get code suggestions

### GitHub Token (Optional)
For enhanced functionality, provide a GitHub Personal Access Token in the sidebar:
- Access private repositories
- Higher rate limits for API calls
- Access to detailed issue information

## 🛠️ Tech Stack

- **UI**: Streamlit
- **Git Operations**: GitPython
- **GitHub API**: PyGithub
- **AI/ML**: Sentence Transformers, FAISS
- **Language Support**: Python, Markdown, YAML, and more

## 📋 Core Functionality

### Repository Analysis
- Clone repositories from GitHub URLs
- Analyze file structure and language distribution
- Identify key configuration and documentation files
- Browse file contents with syntax highlighting

### GitHub Integration
- Fetch open issues with full metadata
- Display issue labels, creation dates, and descriptions
- Direct links to GitHub for detailed issue management

### AI Assistant
- Pattern-based code suggestions
- Common development task recommendations
- Error handling and logging suggestions
- Testing and documentation advice

## 🔄 Example Workflows

1. **Analyze a New Repository**:
   - Enter repository URL
   - Review structure analysis
   - Browse key files
   - Check open issues

2. **Get Code Suggestions**:
   - Ask in chat: "How to add logging?"
   - Ask: "Need help with error handling"
   - Ask: "Add tests to this function"

3. **Understand Issues**:
   - Fetch repository issues
   - Review issue descriptions and labels
   - Use chat to discuss potential solutions

## 🚧 Limitations

- Basic pattern-matching for code suggestions (no advanced LLM integration yet)
- File size limit of 50KB for content display
- Limited to first 50 files in file explorer
- GitHub API rate limiting without token

## 🎯 Future Enhancements

- Advanced AI models for better code understanding
- Pull request management
- CI/CD integration
- Code diff analysis
- Automated fix suggestions

## 📝 License

Open Source - MIT License

## 🤝 Contributing

Feel free to submit issues and enhancement requests! 