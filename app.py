import streamlit as st
import os
import git
import tempfile
from pathlib import Path
import requests
from github import Github
from typing import List, Dict, Any
import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from datetime import datetime

# Page config
st.set_page_config(
    page_title="MCP Agent - AI Git Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'repo_path' not in st.session_state:
    st.session_state.repo_path = None
if 'repo_data' not in st.session_state:
    st.session_state.repo_data = {}
if 'github_token' not in st.session_state:
    st.session_state.github_token = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

class MCPAgent:
    def __init__(self, github_token=None):
        self.github_token = github_token
        self.github = Github(github_token) if github_token else None
        self.model = None
        self.index = None
        self.file_contents = []
        
    def clone_repository(self, repo_url: str) -> str:
        """Clone GitHub repository to temporary directory"""
        try:
            temp_dir = tempfile.mkdtemp()
            git.Repo.clone_from(repo_url, temp_dir)
            return temp_dir
        except Exception as e:
            st.error(f"Error cloning repository: {str(e)}")
            return None
    
    def analyze_repository_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze repository structure and extract key information"""
        try:
            repo_info = {
                'files': [],
                'structure': {},
                'languages': {},
                'total_files': 0,
                'key_files': []
            }
            
            # Walk through repository
            for root, dirs, files in os.walk(repo_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                        
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)
                    
                    # Get file extension
                    ext = Path(file).suffix.lower()
                    if ext:
                        repo_info['languages'][ext] = repo_info['languages'].get(ext, 0) + 1
                    
                    repo_info['files'].append(rel_path)
                    repo_info['total_files'] += 1
                    
                    # Identify key files
                    if file.lower() in ['readme.md', 'requirements.txt', 'setup.py', 'pyproject.toml', 
                                       'dockerfile', 'docker-compose.yml', '.github', 'main.py', 'app.py']:
                        repo_info['key_files'].append(rel_path)
            
            return repo_info
        except Exception as e:
            st.error(f"Error analyzing repository: {str(e)}")
            return {}
    
    def read_file_content(self, file_path: str, max_size: int = 50000) -> str:
        """Read file content with size limit"""
        try:
            if os.path.getsize(file_path) > max_size:
                return f"File too large (>{max_size} bytes)"
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def get_github_issues(self, repo_url: str) -> List[Dict]:
        """Fetch GitHub issues for repository"""
        try:
            if not self.github:
                return []
            
            # Extract owner/repo from URL
            parts = repo_url.replace('https://github.com/', '').strip('/')
            owner, repo_name = parts.split('/')
            
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            issues = []
            
            for issue in repo.get_issues(state='open')[:10]:  # Get first 10 issues
                issues.append({
                    'number': issue.number,
                    'title': issue.title,
                    'body': issue.body[:500] if issue.body else "",
                    'labels': [label.name for label in issue.labels],
                    'created_at': issue.created_at.strftime('%Y-%m-%d'),
                    'url': issue.html_url
                })
            
            return issues
        except Exception as e:
            st.error(f"Error fetching GitHub issues: {str(e)}")
            return []
    
    def generate_code_suggestions(self, context: str, query: str) -> str:
        """Generate simple code suggestions based on patterns"""
        suggestions = []
        
        # Common patterns and suggestions
        if 'test' in query.lower():
            suggestions.append("Consider adding unit tests using pytest:\n```python\ndef test_function():\n    assert True\n```")
        
        if 'docstring' in query.lower() or 'documentation' in query.lower():
            suggestions.append("Add docstrings to functions:\n```python\ndef function_name(param):\n    \"\"\"\n    Description of function.\n    \n    Args:\n        param: Description of parameter\n    \n    Returns:\n        Description of return value\n    \"\"\"\n    pass\n```")
        
        if 'error' in query.lower() or 'exception' in query.lower():
            suggestions.append("Add proper error handling:\n```python\ntry:\n    # your code here\n    pass\nexcept Exception as e:\n    logger.error(f'Error: {e}')\n    raise\n```")
        
        if 'logging' in query.lower():
            suggestions.append("Add logging:\n```python\nimport logging\n\nlogger = logging.getLogger(__name__)\nlogger.info('Your message here')\n```")
        
        return "\n\n".join(suggestions) if suggestions else "No specific suggestions for this query."

# Streamlit UI
def main():
    st.title("🤖 MCP Agent - AI Git Assistant")
    st.subheader("Open-Source AI Developer Assistant")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # GitHub token input
        github_token = st.text_input(
            "GitHub Token (Optional)", 
            type="password",
            help="For accessing private repos and issues API"
        )
        st.session_state.github_token = github_token
        
        st.markdown("---")
        st.markdown("### Features")
        st.markdown("✅ Repository Cloning")
        st.markdown("✅ Structure Analysis") 
        st.markdown("✅ GitHub Issues API")
        st.markdown("✅ Code Suggestions")
        st.markdown("✅ Chat Interface")
    
    # Initialize agent
    agent = MCPAgent(github_token)
    
    # Main interface tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Repository", "Issues", "Analysis", "Chat"])
    
    with tab1:
        st.header("📂 Repository Management")
        
        # Repository URL input
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/owner/repo"
        )
        
        if st.button("Clone & Analyze Repository"):
            if repo_url:
                with st.spinner("Cloning repository..."):
                    repo_path = agent.clone_repository(repo_url)
                    
                if repo_path:
                    st.session_state.repo_path = repo_path
                    
                    with st.spinner("Analyzing repository structure..."):
                        repo_data = agent.analyze_repository_structure(repo_path)
                        st.session_state.repo_data = repo_data
                    
                    st.success("Repository cloned and analyzed successfully!")
        
        # Display repository info
        if st.session_state.repo_data:
            data = st.session_state.repo_data
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Files", data.get('total_files', 0))
            with col2:
                st.metric("Languages", len(data.get('languages', {})))
            with col3:
                st.metric("Key Files", len(data.get('key_files', [])))
            
            # Language breakdown
            if data.get('languages'):
                st.subheader("Language Distribution")
                langs = data['languages']
                st.bar_chart(langs)
            
            # Key files
            if data.get('key_files'):
                st.subheader("Key Files Found")
                for file in data['key_files']:
                    st.code(file)
    
    with tab2:
        st.header("🐛 GitHub Issues")
        
        if repo_url and st.button("Fetch Issues"):
            with st.spinner("Fetching GitHub issues..."):
                issues = agent.get_github_issues(repo_url)
                
            if issues:
                st.success(f"Found {len(issues)} open issues")
                
                for issue in issues:
                    with st.expander(f"Issue #{issue['number']}: {issue['title']}"):
                        st.markdown(f"**Created:** {issue['created_at']}")
                        st.markdown(f"**Labels:** {', '.join(issue['labels'])}")
                        st.markdown(f"**Description:**\n{issue['body']}")
                        st.markdown(f"[View on GitHub]({issue['url']})")
            else:
                st.info("No issues found or unable to fetch issues")
    
    with tab3:
        st.header("🔍 Repository Analysis")
        
        if st.session_state.repo_path and st.session_state.repo_data:
            repo_path = st.session_state.repo_path
            
            # File explorer
            st.subheader("File Explorer")
            selected_file = st.selectbox(
                "Select a file to view:",
                st.session_state.repo_data.get('files', [])[:50]  # Limit to first 50 files
            )
            
            if selected_file:
                file_path = os.path.join(repo_path, selected_file)
                content = agent.read_file_content(file_path)
                
                st.subheader(f"Content: {selected_file}")
                st.code(content, language="python" if selected_file.endswith('.py') else None)
        else:
            st.info("Please clone a repository first in the Repository tab")
    
    with tab4:
        st.header("💬 AI Assistant Chat")
        
        # Chat interface
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Chat input
        user_input = st.chat_input("Ask about the repository, request code suggestions, or get help...")
        
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Generate response
            context = f"Repository data: {st.session_state.repo_data}" if st.session_state.repo_data else "No repository loaded"
            response = agent.generate_code_suggestions(context, user_input)
            
            # Add assistant response to history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # Rerun to display new messages
            st.rerun()

if __name__ == "__main__":
    main() 