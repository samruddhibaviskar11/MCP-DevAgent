import streamlit as st
import os
import git
import tempfile
from pathlib import Path
import requests
from github import Github
from typing import List, Dict, Any
import json
from datetime import datetime

# Fast mode - skip heavy AI imports
FAST_MODE = os.getenv('FAST_MODE', '0') == '1'

if not FAST_MODE:
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        import numpy as np
        AI_IMPORTS_AVAILABLE = True
        AI_MODE_MESSAGE = None
    except ImportError:
        AI_IMPORTS_AVAILABLE = False
        AI_MODE_MESSAGE = "warning"
else:
    AI_IMPORTS_AVAILABLE = False
    AI_MODE_MESSAGE = "fast_mode"

# Page config
st.set_page_config(
    page_title="MCP Agent - AI Git Assistant",
    page_icon="🤖",
    layout="wide"
)

# Show AI mode messages after page config
if AI_MODE_MESSAGE == "warning":
    st.warning("⚡ Running in fast mode - AI features disabled")
elif AI_MODE_MESSAGE == "fast_mode":
    st.info("⚡ Fast mode enabled - AI features disabled for speed")

# Initialize session state
if 'repo_path' not in st.session_state:
    st.session_state.repo_path = None
if 'repo_data' not in st.session_state:
    st.session_state.repo_data = {}
if 'github_token' not in st.session_state:
    st.session_state.github_token = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'github_data' not in st.session_state:
    st.session_state.github_data = {}

class MCPAgent:
    def __init__(self, github_token=None):
        self.github_token = github_token
        if github_token and AI_IMPORTS_AVAILABLE:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.model = None

    def clone_repository(self, repo_url: str) -> str:
        """Clone a GitHub repository to a temporary directory"""
        try:
            temp_dir = tempfile.mkdtemp()
            repo = git.Repo.clone_from(repo_url, temp_dir)
            st.success(f"Repository cloned to: {temp_dir}")
            return temp_dir
        except Exception as e:
            st.error(f"Failed to clone repository: {str(e)}")
            return None

    def analyze_repository_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze the structure of a cloned repository"""
        structure = {
            'total_files': 0,
            'directories': [],
            'files_by_type': {},
            'languages': {},
            'key_files': [],
            'size_mb': 0
        }
        
        try:
            # Walk through repository
            for root, dirs, files in os.walk(repo_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                rel_root = os.path.relpath(root, repo_path)
                if rel_root != '.':
                    structure['directories'].append(rel_root)
                
                for file in files:
                    if file.startswith('.'):
                        continue
                        
                    structure['total_files'] += 1
                    file_path = os.path.join(root, file)
                    
                    # File size
                    try:
                        size = os.path.getsize(file_path)
                        structure['size_mb'] += size / (1024 * 1024)
                    except:
                        pass
                    
                    # File extension analysis
                    _, ext = os.path.splitext(file)
                    if ext:
                        ext = ext.lower()
                        structure['files_by_type'][ext] = structure['files_by_type'].get(ext, 0) + 1
                        
                        # Language mapping
                        lang_map = {
                            '.py': 'Python', '.js': 'JavaScript', '.jsx': 'React',
                            '.ts': 'TypeScript', '.tsx': 'TypeScript React',
                            '.java': 'Java', '.cpp': 'C++', '.c': 'C',
                            '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS',
                            '.md': 'Markdown', '.json': 'JSON', '.yaml': 'YAML',
                            '.yml': 'YAML', '.xml': 'XML', '.sql': 'SQL'
                        }
                        
                        if ext in lang_map:
                            lang = lang_map[ext]
                            structure['languages'][lang] = structure['languages'].get(lang, 0) + 1
                    
                    # Identify key files
                    key_patterns = [
                        'readme', 'license', 'makefile', 'dockerfile',
                        'requirements.txt', 'package.json', 'pom.xml',
                        'cargo.toml', 'go.mod', 'setup.py'
                    ]
                    
                    if any(pattern in file.lower() for pattern in key_patterns):
                        rel_path = os.path.relpath(file_path, repo_path)
                        structure['key_files'].append(rel_path)
            
            structure['size_mb'] = round(structure['size_mb'], 2)
            return structure
            
        except Exception as e:
            st.error(f"Error analyzing repository: {str(e)}")
            return structure

    def analyze_code_file(self, file_path: str) -> Dict[str, int]:
        """Analyze a code file for basic metrics"""
        metrics = {
            'lines': 0,
            'functions': 0,
            'classes': 0,
            'imports': 0,
            'comments': 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                metrics['lines'] = len(lines)
                
                # Basic pattern matching for different languages
                for line in lines:
                    line = line.strip()
                    
                    # Python patterns
                    if line.startswith('def ') or line.startswith('async def '):
                        metrics['functions'] += 1
                    elif line.startswith('class '):
                        metrics['classes'] += 1
                    elif line.startswith('import ') or line.startswith('from '):
                        metrics['imports'] += 1
                    elif line.startswith('#'):
                        metrics['comments'] += 1
                    
                    # JavaScript patterns
                    elif 'function ' in line or '=>' in line:
                        metrics['functions'] += 1
                    elif line.startswith('//') or '/*' in line:
                        metrics['comments'] += 1
        
        except Exception:
            pass
            
        return metrics

    def extract_dependencies(self, file_path: str, ext: str) -> List[str]:
        """Extract dependencies from common files"""
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                if 'requirements.txt' in file_path:
                    dependencies = [line.strip().split('==')[0].split('>=')[0] 
                                  for line in content.split('\n') if line.strip()]
                
                elif 'package.json' in file_path:
                    try:
                        package_data = json.loads(content)
                        deps = package_data.get('dependencies', {})
                        dev_deps = package_data.get('devDependencies', {})
                        dependencies = list(deps.keys()) + list(dev_deps.keys())
                    except:
                        pass
                
                elif ext == '.py':
                    import re
                    import_pattern = r'(?:from\s+(\S+)\s+import|import\s+(\S+))'
                    matches = re.findall(import_pattern, content)
                    dependencies = [match[0] or match[1] for match in matches]
        
        except Exception:
            pass
            
        return dependencies[:10]  # Limit to top 10

    def extract_python_imports(self, repo_path: str) -> Dict[str, List[str]]:
        """Extract Python imports from all Python files"""
        imports_map = {}
        
        try:
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, repo_path)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                            import re
                            import_pattern = r'(?:from\s+(\S+)\s+import|import\s+(\S+))'
                            matches = re.findall(import_pattern, content)
                            file_imports = [match[0] or match[1] for match in matches]
                            
                            if file_imports:
                                imports_map[rel_path] = file_imports[:5]  # Top 5 imports
                                
                        except Exception:
                            continue
                            
        except Exception as e:
            st.error(f"Error extracting imports: {str(e)}")
            
        return imports_map

    def read_file_content(self, file_path: str, max_size: int = 50000) -> str:
        """Read and return file content with size limit"""
        try:
            file_size = os.path.getsize(file_path)
            if file_size > max_size:
                return f"File too large ({file_size} bytes). Showing first {max_size} characters:\n\n" + \
                       open(file_path, 'r', encoding='utf-8', errors='ignore').read(max_size)
            else:
                return open(file_path, 'r', encoding='utf-8', errors='ignore').read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def validate_github_token(self) -> bool:
        """Validate GitHub token"""
        if not self.github_token:
            return False
        
        try:
            g = Github(self.github_token)
            user = g.get_user()
            return True
        except Exception:
            return False

    def get_token_info(self) -> Dict:
        """Get information about the GitHub token (robust across PyGithub versions)"""
        if not self.github_token:
            return {"valid": False}
        
        try:
            g = Github(self.github_token)
            user = g.get_user()
            # Token is valid if we can fetch the user login
            username = getattr(user, 'login', None)
            remaining = None
            reset_time = None

            try:
                rl = g.get_rate_limit()
                # Try modern attributes
                core = getattr(rl, 'core', None)
                if core is not None:
                    remaining = getattr(core, 'remaining', None)
                    reset_time = getattr(core, 'reset', None)
                else:
                    # Fallback to raw_data shape
                    raw = getattr(rl, 'raw_data', None)
                    if isinstance(raw, dict):
                        core_raw = (raw.get('resources', {}) or {}).get('core', {}) or {}
                        remaining = core_raw.get('remaining')
                        reset_time = core_raw.get('reset')
            except Exception:
                pass
            
            return {
                "valid": True,
                "username": username,
                "remaining_requests": remaining,
                "reset_time": reset_time
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def extract_repo_info(self, repo_url: str) -> tuple:
        """Extract owner and repo name from GitHub URL"""
        try:
            # Handle different GitHub URL formats
            if 'github.com/' in repo_url:
                parts = repo_url.split('github.com/')[-1].split('/')
                if len(parts) >= 2:
                    owner = parts[0]
                    repo = parts[1].replace('.git', '')
                    return owner, repo
        except Exception:
            pass
        return None, None

    def get_github_issues(self, repo_url: str, state: str = 'open', limit: int = 50) -> List[Dict]:
        """Fetch GitHub issues for a repository"""
        owner, repo = self.extract_repo_info(repo_url)
        if not owner or not repo:
            return []
        
        issues = []
        try:
            if self.github_token:
                g = Github(self.github_token)
            else:
                g = Github()
            
            repository = g.get_repo(f"{owner}/{repo}")
            github_issues = repository.get_issues(state=state)
            
            count = 0
            for issue in github_issues:
                if count >= limit:
                    break
                
                # Skip pull requests (they appear in issues)
                if issue.pull_request:
                    continue
                
                issues.append({
                    'number': issue.number,
                    'title': issue.title,
                    'body': issue.body[:500] if issue.body else "",
                    'state': issue.state,
                    'created_at': issue.created_at.strftime('%Y-%m-%d %H:%M'),
                    'updated_at': issue.updated_at.strftime('%Y-%m-%d %H:%M'),
                    'author': issue.user.login,
                    'labels': [label.name for label in issue.labels],
                    'comments': issue.comments,
                    'url': issue.html_url
                })
                count += 1
                
        except Exception as e:
            st.error(f"Error fetching issues: {str(e)}")
            
        return issues

    def get_github_pull_requests(self, repo_url: str, state: str = 'open', limit: int = 50) -> List[Dict]:
        """Fetch GitHub pull requests for a repository"""
        owner, repo = self.extract_repo_info(repo_url)
        if not owner or not repo:
            return []
        
        prs = []
        try:
            if self.github_token:
                g = Github(self.github_token)
            else:
                g = Github()
            
            repository = g.get_repo(f"{owner}/{repo}")
            github_prs = repository.get_pulls(state=state)
            
            count = 0
            for pr in github_prs:
                if count >= limit:
                    break
                
                prs.append({
                    'number': pr.number,
                    'title': pr.title,
                    'body': pr.body[:500] if pr.body else "",
                    'state': pr.state,
                    'created_at': pr.created_at.strftime('%Y-%m-%d %H:%M'),
                    'updated_at': pr.updated_at.strftime('%Y-%m-%d %H:%M'),
                    'author': pr.user.login,
                    'base_branch': pr.base.ref,
                    'head_branch': pr.head.ref,
                    'mergeable': pr.mergeable,
                    'url': pr.html_url
                })
                count += 1
                
        except Exception as e:
            st.error(f"Error fetching pull requests: {str(e)}")
            
        return prs

    def get_github_data(self, repo_url: str, include_closed: bool = False, limit: int = 50) -> Dict[str, List]:
        """Get comprehensive GitHub data"""
        data = {
            'issues': [],
            'pull_requests': []
        }
        
        # Fetch open items
        data['issues'] = self.get_github_issues(repo_url, 'open', limit)
        data['pull_requests'] = self.get_github_pull_requests(repo_url, 'open', limit)
        
        # Fetch closed items if requested
        if include_closed:
            closed_issues = self.get_github_issues(repo_url, 'closed', limit // 2)
            closed_prs = self.get_github_pull_requests(repo_url, 'closed', limit // 2)
            data['issues'].extend(closed_issues)
            data['pull_requests'].extend(closed_prs)
        
        return data

    def generate_ai_response(self, context: str, query: str, repo_data: dict, github_data: dict = None) -> str:
        """Generate AI response using pattern matching (fallback when AI unavailable)"""
        query_lower = query.lower()
        
        # Classify the query type
        query_type = self.classify_query(query_lower)
        
        # Build context information
        context_info = self.build_context_info(repo_data, github_data)
        
        # Generate response based on query type
        if query_type == 'structure':
            return self.handle_structure_query(query, context_info, repo_data)
        elif query_type == 'code_analysis':
            return self.handle_code_analysis_query(query, context_info, repo_data)
        elif query_type == 'issues':
            return self.handle_issues_query(query, context_info, github_data)
        elif query_type == 'suggestions':
            return self.handle_suggestions_query(query, context_info, repo_data)
        elif query_type == 'files':
            return self.handle_files_query(query, context_info, repo_data)
        elif query_type == 'dependencies':
            return self.handle_dependencies_query(query, context_info, repo_data)
        else:
            return self.handle_general_query(query, context_info, repo_data)

    def classify_query(self, query_lower: str) -> str:
        """Classify user query into categories"""
        structure_keywords = ['structure', 'organization', 'folders', 'directories', 'layout', 'architecture']
        code_keywords = ['functions', 'classes', 'methods', 'code', 'implementation', 'logic']
        issue_keywords = ['issues', 'bugs', 'problems', 'tickets', 'github']
        suggestion_keywords = ['suggest', 'recommend', 'improve', 'optimize', 'best practices']
        file_keywords = ['files', 'show me', 'content', 'read', 'view']
        dependency_keywords = ['dependencies', 'imports', 'packages', 'libraries', 'requirements']
        
        keyword_map = {
            'structure': structure_keywords,
            'code_analysis': code_keywords,
            'issues': issue_keywords,
            'suggestions': suggestion_keywords,
            'files': file_keywords,
            'dependencies': dependency_keywords
        }
        
        for category, keywords in keyword_map.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return 'general'

    def build_context_info(self, repo_data: dict, github_data: dict = None) -> dict:
        """Build context information for response generation"""
        context = {
            'has_repo': bool(repo_data),
            'total_files': repo_data.get('total_files', 0),
            'languages': list(repo_data.get('languages', {}).keys()),
            'key_files': repo_data.get('key_files', []),
            'size_mb': repo_data.get('size_mb', 0),
            'has_github_data': bool(github_data),
            'open_issues': len(github_data.get('issues', [])) if github_data else 0,
            'open_prs': len(github_data.get('pull_requests', [])) if github_data else 0
        }
        return context

    def handle_structure_query(self, query: str, context: dict, repo_data: dict) -> str:
        """Handle repository structure related queries"""
        if not context['has_repo']:
            return "Please clone a repository first to analyze its structure."
        
        response = f"📂 **Repository Structure Analysis**\n\n"
        response += f"• **Total Files:** {context['total_files']}\n"
        response += f"• **Repository Size:** {context['size_mb']} MB\n"
        response += f"• **Programming Languages:** {', '.join(context['languages'])}\n\n"
        
        if context['key_files']:
            response += f"🔑 **Key Files Found:**\n"
            for file in context['key_files'][:5]:
                response += f"• {file}\n"
            response += "\n"
        
        directories = repo_data.get('directories', [])
        if directories:
            response += f"📁 **Directory Structure:**\n"
            for directory in directories[:10]:
                response += f"• {directory}\n"
        
        return response

    def handle_code_analysis_query(self, query: str, context: dict, repo_data: dict) -> str:
        """Handle code analysis related queries"""
        if not context['has_repo']:
            return "Please clone a repository first to analyze the code."
        
        response = f"🔍 **Code Analysis**\n\n"
        
        languages = repo_data.get('languages', {})
        if languages:
            response += f"**Language Distribution:**\n"
            for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                response += f"• {lang}: {count} files\n"
            response += "\n"
        
        files_by_type = repo_data.get('files_by_type', {})
        if files_by_type:
            response += f"**File Types:**\n"
            for ext, count in sorted(files_by_type.items(), key=lambda x: x[1], reverse=True)[:5]:
                response += f"• {ext}: {count} files\n"
        
        response += f"\n💡 **Suggestions:**\n"
        response += f"• Use the Analysis tab to browse individual files\n"
        response += f"• Check key configuration files like requirements.txt or package.json\n"
        response += f"• Look for documentation in README files\n"
        
        return response

    def handle_issues_query(self, query: str, context: dict, github_data: dict) -> str:
        """Handle GitHub issues related queries"""
        if not context['has_github_data']:
            return "Please fetch GitHub data first using the Issues tab."
        
        issues = github_data.get('issues', [])
        
        response = f"🐛 **GitHub Issues Analysis**\n\n"
        response += f"• **Open Issues:** {len([i for i in issues if i['state'] == 'open'])}\n"
        response += f"• **Total Issues:** {len(issues)}\n\n"
        
        if issues:
            response += f"**Recent Issues:**\n"
            for issue in issues[:3]:
                response += f"• #{issue['number']}: {issue['title'][:50]}...\n"
                response += f"  Created: {issue['created_at']} by {issue['author']}\n\n"
        
        # Analyze issue labels
        all_labels = []
        for issue in issues:
            all_labels.extend(issue.get('labels', []))
        
        if all_labels:
            from collections import Counter
            label_counts = Counter(all_labels)
            response += f"**Common Labels:**\n"
            for label, count in label_counts.most_common(5):
                response += f"• {label}: {count} issues\n"
        
        return response

    def handle_suggestions_query(self, query: str, context: dict, repo_data: dict) -> str:
        """Handle improvement suggestions"""
        if not context['has_repo']:
            return "Please clone a repository first to get suggestions."
        
        response = f"💡 **Improvement Suggestions**\n\n"
        
        # Check for common files
        key_files = context['key_files']
        suggestions = []
        
        if not any('readme' in f.lower() for f in key_files):
            suggestions.append("📝 Consider adding a README.md file for documentation")
        
        if not any('license' in f.lower() for f in key_files):
            suggestions.append("⚖️ Consider adding a LICENSE file")
        
        if context['languages']:
            if 'Python' in context['languages']:
                if not any('requirements.txt' in f for f in key_files):
                    suggestions.append("🐍 Consider adding requirements.txt for Python dependencies")
            
            if 'JavaScript' in context['languages']:
                if not any('package.json' in f for f in key_files):
                    suggestions.append("📦 Consider adding package.json for JavaScript dependencies")
        
        if context['size_mb'] > 100:
            suggestions.append("📏 Large repository - consider splitting into smaller modules")
        
        if context['total_files'] > 1000:
            suggestions.append("📂 Many files - ensure good directory organization")
        
        if suggestions:
            for suggestion in suggestions:
                response += f"• {suggestion}\n"
        else:
            response += "✅ Repository looks well organized!\n"
        
        response += f"\n**General Best Practices:**\n"
        response += f"• Keep files under 500 lines when possible\n"
        response += f"• Use clear, descriptive file and directory names\n"
        response += f"• Include comments and documentation\n"
        response += f"• Follow language-specific conventions\n"
        
        return response

    def handle_files_query(self, query: str, context: dict, repo_data: dict) -> str:
        """Handle file-related queries"""
        if not context['has_repo']:
            return "Please clone a repository first to browse files."
        
        response = f"📄 **File Information**\n\n"
        
        # Show key files
        if context['key_files']:
            response += f"**Important Files:**\n"
            for file in context['key_files']:
                response += f"• {file}\n"
            response += "\n"
        
        # Show file types
        files_by_type = repo_data.get('files_by_type', {})
        if files_by_type:
            response += f"**File Types Distribution:**\n"
            for ext, count in sorted(files_by_type.items(), key=lambda x: x[1], reverse=True)[:8]:
                response += f"• {ext}: {count} files\n"
        
        response += f"\n💡 **Navigation Tips:**\n"
        response += f"• Use the Analysis tab to browse and read files\n"
        response += f"• Look for configuration files in the root directory\n"
        response += f"• Check documentation files for project information\n"
        
        return response

    def handle_dependencies_query(self, query: str, context: dict, repo_data: dict) -> str:
        """Handle dependency-related queries"""
        if not context['has_repo']:
            return "Please clone a repository first to analyze dependencies."
        
        response = f"📦 **Dependencies Analysis**\n\n"
        
        key_files = context['key_files']
        dep_files = [f for f in key_files if any(dep in f.lower() 
                    for dep in ['requirements', 'package.json', 'pom.xml', 'cargo.toml'])]
        
        if dep_files:
            response += f"**Dependency Files Found:**\n"
            for file in dep_files:
                response += f"• {file}\n"
            response += "\n"
        else:
            response += "No standard dependency files found.\n\n"
        
        if 'Python' in context['languages']:
            response += f"🐍 **Python Project:**\n"
            response += f"• Look for requirements.txt or setup.py\n"
            response += f"• Check for Pipfile or pyproject.toml\n\n"
        
        if 'JavaScript' in context['languages']:
            response += f"📦 **JavaScript/Node.js Project:**\n"
            response += f"• Look for package.json and package-lock.json\n"
            response += f"• Check for yarn.lock if using Yarn\n\n"
        
        response += f"💡 **Tips:**\n"
        response += f"• Use the Analysis tab to view dependency files\n"
        response += f"• Check for security vulnerabilities in dependencies\n"
        response += f"• Keep dependencies up to date\n"
        
        return response

    def handle_general_query(self, query: str, context: dict, repo_data: dict) -> str:
        """Handle general queries"""
        response = f"🤖 **MCP Agent Assistant**\n\n"
        
        if context['has_repo']:
            response += f"I can help you analyze this repository with {context['total_files']} files "
            response += f"in {len(context['languages'])} programming languages.\n\n"
        else:
            response += f"I can help you analyze GitHub repositories! Start by cloning a repository.\n\n"
        
        response += f"**What I can help with:**\n"
        response += f"• 📂 Repository structure and organization\n"
        response += f"• 🔍 Code analysis and file exploration\n"
        response += f"• 🐛 GitHub issues and pull requests\n"
        response += f"• 💡 Code improvement suggestions\n"
        response += f"• 📦 Dependency analysis\n"
        response += f"• 📄 File content viewing\n\n"
        
        response += f"**Try asking:**\n"
        response += f"• 'Show me the repository structure'\n"
        response += f"• 'What programming languages are used?'\n"
        response += f"• 'Analyze the code organization'\n"
        response += f"• 'What are the main files?'\n"
        
        return response

    def generate_contextual_response(self, query: str, context: dict, repo_data: dict) -> str:
        """Generate contextual response based on available data"""
        # Use AI model if available, otherwise fall back to pattern matching
        if self.model and AI_IMPORTS_AVAILABLE:
            # AI-enhanced response would go here
            pass
        
        # Pattern-based response
        return self.generate_ai_response(context, query, repo_data)

    # ===== New helper methods: search, PR summary, security scan =====
    def collect_text_files(self, repo_path: str) -> List[str]:
        allowed_exts = {'.py', '.js', '.jsx', '.ts', '.tsx', '.md', '.json', '.yaml', '.yml', '.html', '.css'}
        text_files = []
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.startswith('.'):
                    continue
                path = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                if ext.lower() in allowed_exts:
                    text_files.append(path)
        return text_files

    def chunk_file_content(self, file_path: str, chunk_size: int = 800, overlap: int = 100) -> List[Dict[str, Any]]:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except Exception:
            return []
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]
            chunks.append({
                'text': chunk_text,
                'file_path': file_path,
                'offset': start
            })
            if end == len(text):
                break
            start = end - overlap
            if start < 0:
                start = 0
        return chunks

    def build_semantic_index(self, repo_path: str) -> bool:
        if not (AI_IMPORTS_AVAILABLE and self.model):
            return False
        # Reuse if already built for same repo
        if st.session_state.get('semantic_index_repo') == repo_path and st.session_state.get('faiss_index') is not None:
            return True
        files = self.collect_text_files(repo_path)
        all_chunks = []
        for fpath in files[:200]:  # cap for speed
            all_chunks.extend(self.chunk_file_content(fpath))
        if not all_chunks:
            return False
        texts = [c['text'] for c in all_chunks]
        embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        # Build FAISS IP index (embeddings already normalized)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)
        st.session_state['faiss_index'] = index
        st.session_state['chunk_texts'] = texts
        st.session_state['chunk_meta'] = all_chunks
        st.session_state['semantic_index_repo'] = repo_path
        return True

    def semantic_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        if not (AI_IMPORTS_AVAILABLE and self.model):
            return []
        index = st.session_state.get('faiss_index')
        if index is None:
            return []
        q = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        dists, idxs = index.search(q, top_k)
        results = []
        for rank, (i, score) in enumerate(zip(idxs[0], dists[0])):
            if i == -1:
                continue
            meta = st.session_state['chunk_meta'][i]
            results.append({
                'file_path': meta['file_path'],
                'offset': meta['offset'],
                'text': st.session_state['chunk_texts'][i],
                'score': float(score)
            })
        return results

    def keyword_search(self, repo_path: str, query: str, max_results: int = 30) -> List[Dict[str, Any]]:
        results = []
        q = query.lower()
        for fpath in self.collect_text_files(repo_path):
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
            except Exception:
                continue
            low = text.lower()
            idx = low.find(q)
            if idx != -1:
                start = max(0, idx - 200)
                end = min(len(text), idx + len(query) + 200)
                snippet = text[start:end]
                results.append({'file_path': fpath, 'offset': start, 'text': snippet})
                if len(results) >= max_results:
                    break
        return results

    def get_pr_diff_summary(self, repo_url: str, pr_number: int) -> Dict[str, Any]:
        owner, repo = self.extract_repo_info(repo_url)
        if not owner or not repo:
            return {}
        try:
            g = Github(self.github_token) if self.github_token else Github()
            repository = g.get_repo(f"{owner}/{repo}")
            pr = repository.get_pull(int(pr_number))
            files = list(pr.get_files())
            changed_files = [f.filename for f in files]
            additions = sum(f.additions for f in files)
            deletions = sum(f.deletions for f in files)
            risk_flags = []
            for name in changed_files:
                lname = name.lower()
                if any(x in lname for x in ['requirements.txt', 'package.json', 'lock', 'dockerfile', 'deployment', 'ci', 'workflow']):
                    risk_flags.append(name)
            return {
                'changed_files': changed_files,
                'additions': additions,
                'deletions': deletions,
                'risk_files': risk_flags
            }
        except Exception as e:
            st.error(f"Error analyzing PR: {str(e)}")
            return {}

    def scan_dependencies(self, repo_path: str) -> List[Dict[str, str]]:
        packages = []
        # requirements.txt
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file == 'requirements.txt':
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line in f:
                                line = line.strip()
                                if not line or line.startswith('#'):
                                    continue
                                name = line
                                version = None
                                for sep in ['==', '>=', '<=', '~=', '!=', '>','<']:
                                    if sep in line:
                                        parts = line.split(sep)
                                        name = parts[0].strip()
                                        version = parts[1].strip() if len(parts) > 1 else None
                                        break
                                packages.append({'name': name, 'version': version, 'ecosystem': 'PyPI'})
                    except Exception:
                        pass
                elif file == 'package.json':
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            pkg = json.load(f)
                        for section in ['dependencies', 'devDependencies']:
                            deps = pkg.get(section, {})
                            for name, ver in deps.items():
                                clean_ver = ver.lstrip('^~>=<') if isinstance(ver, str) else None
                                packages.append({'name': name, 'version': clean_ver, 'ecosystem': 'npm'})
                    except Exception:
                        pass
        return packages

    def query_osv(self, packages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        if not packages:
            return []
        queries = []
        for p in packages[:200]:  # cap for speed
            q = {
                'package': {
                    'name': p['name'],
                    'ecosystem': 'PyPI' if p['ecosystem'] == 'PyPI' else 'npm'
                }
            }
            if p.get('version'):
                q['version'] = p['version']
            queries.append(q)
        try:
            resp = requests.post('https://api.osv.dev/v1/querybatch', json={'queries': queries}, timeout=20)
            data = resp.json()
            vulns = []
            for item in data.get('results', []):
                for v in item.get('vulns', []) or []:
                    vulns.append({
                        'id': v.get('id'),
                        'summary': v.get('summary') or v.get('details', '')[:140],
                        'severity': (v.get('severity') or [{}])[0].get('score') if v.get('severity') else None,
                        'aliases': v.get('aliases', []),
                        'references': v.get('references', [])
                    })
            return vulns
        except Exception as e:
            st.error(f"OSV query failed: {str(e)}")
            return []

    # ===== Repo analysis helpers (FAST_MODE-friendly) =====
    def get_top_files_by_size(self, repo_path: str, limit: int = 10) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.startswith('.'):
                    continue
                path = os.path.join(root, file)
                try:
                    size = os.path.getsize(path)
                except Exception:
                    continue
                items.append({
                    'path': os.path.relpath(path, repo_path),
                    'size_bytes': size
                })
        items.sort(key=lambda x: x['size_bytes'], reverse=True)
        return items[:limit]

    def get_top_code_files_by_lines(self, repo_path: str, limit: int = 10) -> List[Dict[str, Any]]:
        code_exts = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp'}
        items: List[Dict[str, Any]] = []
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.startswith('.'):
                    continue
                _, ext = os.path.splitext(file)
                if ext.lower() not in code_exts:
                    continue
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    num = len(lines)
                except Exception:
                    continue
                items.append({
                    'path': os.path.relpath(path, repo_path),
                    'lines': num
                })
        items.sort(key=lambda x: x['lines'], reverse=True)
        return items[:limit]

    def scan_todos(self, repo_path: str, keywords: List[str] = None, max_per_file: int = 20) -> Dict[str, List[str]]:
        if keywords is None:
            keywords = ['TODO', 'FIXME', 'HACK']
        results: Dict[str, List[str]] = {}
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.startswith('.'):
                    continue
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        for idx, line in enumerate(f.readlines(), start=1):
                            if any(k in line for k in keywords):
                                rel = os.path.relpath(path, repo_path)
                                results.setdefault(rel, [])
                                if len(results[rel]) < max_per_file:
                                    # Trim line for display
                                    snippet = line.strip()
                                    if len(snippet) > 200:
                                        snippet = snippet[:200] + '...'
                                    results[rel].append(f"L{idx}: {snippet}")
                except Exception:
                    continue
        return results

    # ===== Code suggestion helpers =====
    def generate_code_suggestions(self, file_path: str) -> str:
        """Generate heuristic code improvement suggestions for a given file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return f"Could not read file: {e}"
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        suggestions: List[str] = []

        # Generic suggestions
        if len(content) > 0 and len(content.splitlines()) > 800:
            suggestions.append("Consider splitting large files into smaller modules for readability.")

        if ext == '.py':
            suggestions.extend(self._suggestions_python(content))
        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
            suggestions.extend(self._suggestions_js_ts(content, ext))
        elif ext == '.md':
            if '# ' not in content[:2000]:
                suggestions.append("Add a top-level heading and table of contents to improve documentation structure.")
        else:
            suggestions.append("No language-specific checks available; consider adding linters/formatters.")

        if not suggestions:
            return "✅ No obvious issues found. Consider running linters for deeper checks."

        bullet_list = "\n".join([f"• {s}" for s in suggestions])
        return f"### Code Suggestions\n\n{bullet_list}"

    def _suggestions_python(self, text: str) -> List[str]:
        suggestions: List[str] = []
        lines = text.splitlines()
        # Heuristics
        if any('print(' in l for l in lines):
            suggestions.append("Replace print statements with the logging module and configurable log levels.")
        if 'except:' in text or 'except Exception' in text:
            suggestions.append("Avoid bare or broad excepts; catch specific exceptions and log/handle appropriately.")
        if any(l.rstrip().endswith('  ') for l in lines):
            suggestions.append("Trim trailing whitespace to keep diffs clean.")
        if any(len(l) > 120 for l in lines[:2000]):
            suggestions.append("Wrap long lines (>120 chars) for readability.")
        if 'TODO' in text or 'FIXME' in text:
            suggestions.append("Resolve TODO/FIXME items or create tracked issues.")
        if 'typing' not in text and 'def ' in text:
            suggestions.append("Consider adding type hints and running mypy for static typing.")
        # Simple docstring check for functions
        import re
        func_defs = [m.start() for m in re.finditer(r'\n\s*def\s+\w+\(', text)]
        for idx in func_defs[:10]:
            after = text[idx: idx + 200]
            if '):\n' in after and '"""' not in after[:120]:
                suggestions.append("Add docstrings to functions for clarity (first line summary, args, returns).")
                break
        return suggestions

    def _suggestions_js_ts(self, text: str, ext: str) -> List[str]:
        suggestions: List[str] = []
        if 'console.log' in text:
            suggestions.append("Replace console.log with a structured logger and appropriate levels.")
        if ' var ' in f" {text} ":
            suggestions.append("Avoid var; use const/let for block scoping.")
        if any(len(l) > 120 for l in text.splitlines()[:2000]):
            suggestions.append("Wrap long lines (>120 chars) for readability.")
        if ext in ['.ts', '.tsx'] and 'any' in text:
            suggestions.append("Avoid using 'any' in TypeScript; prefer precise types.")
        if 'TODO' in text or 'FIXME' in text:
            suggestions.append("Resolve TODO/FIXME items or create tracked issues.")
        return suggestions

    def build_repo_tree(self, repo_path: str, max_depth: int = 3, max_entries: int = 800) -> str:
        """Return an ASCII tree of the repository up to a given depth and entry count."""
        from itertools import islice
        total_count = 0
        lines: List[str] = []

        def safe_listdir(path: str) -> List[str]:
            try:
                return sorted([p for p in os.listdir(path) if not p.startswith('.')])
            except Exception:
                return []

        def render_dir(path: str, prefix: str, depth: int):
            nonlocal total_count
            if depth > max_depth or total_count >= max_entries:
                return
            entries = safe_listdir(path)
            files = [e for e in entries if os.path.isfile(os.path.join(path, e))]
            dirs = [e for e in entries if os.path.isdir(os.path.join(path, e))]
            ordered = dirs + files
            count = len(ordered)
            for idx, name in enumerate(ordered):
                if total_count >= max_entries:
                    break
                connector = '└── ' if idx == count - 1 else '├── '
                line = f"{prefix}{connector}{name}"
                lines.append(line)
                total_count += 1
                full = os.path.join(path, name)
                if os.path.isdir(full):
                    extension = '    ' if idx == count - 1 else '│   '
                    render_dir(full, prefix + extension, depth + 1)

        root_name = os.path.basename(repo_path.rstrip(os.sep)) or os.path.basename(repo_path)
        lines.append(f"{root_name}/")
        render_dir(repo_path, '', 1)
        if total_count >= max_entries:
            lines.append(f"... (truncated after {max_entries} entries)")
        return "\n".join(lines)

# Streamlit UI

def main():
    st.title("🤖 MCP Agent - AI Git Assistant")
    st.subheader("Open-Source AI Developer Assistant")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # GitHub token input
        github_token = st.text_input(
            "GitHub Personal Access Token (Optional)",
            type="password",
            value=st.session_state.github_token,
            help="Required for private repos and higher rate limits"
        )
        
        if github_token != st.session_state.github_token:
            st.session_state.github_token = (github_token or "").strip()
        
        # Initialize agent
        agent = MCPAgent(github_token.strip() if github_token else None)
        
        # Token validation
        if github_token:
            token_info = agent.get_token_info()
            if token_info.get("valid"):
                st.success(f"✅ Token valid - User: {token_info.get('username')}")
                st.info(f"API Requests: {token_info.get('remaining_requests')}")
            else:
                st.error(f"❌ Invalid token: {token_info.get('error','unknown error')}")
        
        st.markdown("---")
        st.markdown("### 🛠️ Quick Setup")
        st.markdown("1. Enter a GitHub repository URL")
        st.markdown("2. Click 'Clone & Analyze'")
        st.markdown("3. Explore using the tabs above")
        
        if not AI_IMPORTS_AVAILABLE:
            st.markdown("---")
            st.warning("⚡ Fast Mode Active")
            st.markdown("Some AI features disabled for quick startup")

    # Initialize agent
    agent = MCPAgent(st.session_state.github_token)

    # Main interface tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Repository", "Issues", "Analysis", "Search", "Chat", "Security"])
    
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
                st.metric("Size (MB)", data.get('size_mb', 0))
            
            # Language distribution
            if data.get('languages'):
                st.subheader("Programming Languages")
                lang_data = data['languages']
                for lang, count in sorted(lang_data.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / sum(lang_data.values())) * 100
                    st.progress(percentage / 100, text=f"{lang}: {count} files ({percentage:.1f}%)")
            
            # Repository tree view
            st.subheader("📁 Repository Tree")
            col_a, col_b = st.columns([1, 3])
            with col_a:
                depth = st.slider("Depth", min_value=1, max_value=8, value=3)
            with col_b:
                if st.button("Show Tree"):
                    with st.spinner("Building repository tree..."):
                        tree_text = agent.build_repo_tree(st.session_state.repo_path, max_depth=depth)
                    st.session_state['repo_tree_text'] = tree_text
            if st.session_state.get('repo_tree_text'):
                st.code(st.session_state['repo_tree_text'], language="text")

            # Key files
            if data.get('key_files'):
                st.subheader("Key Files")
                for file in data['key_files']:
                    st.write(f"📄 {file}")

    with tab2:
        st.header("🐛 GitHub Issues & Pull Requests")
        
        if st.session_state.repo_path:
            # Get repository URL from user or detect from clone
            if 'repo_url' in locals() and repo_url:
                current_repo_url = repo_url
            else:
                current_repo_url = st.text_input("Repository URL", placeholder="https://github.com/owner/repo")
            
            if current_repo_url:
                col1, col2 = st.columns(2)
                with col1:
                    include_closed = st.checkbox("Include closed items")
                with col2:
                    limit = st.number_input("Limit", min_value=10, max_value=100, value=20)
                
                if st.button("Fetch GitHub Data"):
                    with st.spinner("Fetching GitHub data..."):
                        github_data = agent.get_github_data(current_repo_url, include_closed, limit)
                        st.session_state.github_data = github_data
                    
                    st.success("GitHub data fetched successfully!")
                
                # Display GitHub data
                if st.session_state.github_data:
                    github_data = st.session_state.github_data
                    
                    # Issues
                    issues = github_data.get('issues', [])
                    if issues:
                        st.subheader(f"📋 Issues ({len(issues)})")
                        for issue in issues[:10]:
                            with st.expander(f"#{issue['number']}: {issue['title'][:60]}..."):
                                col_a, col_b = st.columns([3, 1])
                                with col_a:
                                    st.write(f"**Created:** {issue['created_at']} by {issue['author']}")
                                    st.write(f"**Status:** {issue['state']}")
                                    if issue['body']:
                                        st.write(f"**Description:** {issue['body'][:200]}...")
                                with col_b:
                                    if issue['labels']:
                                        st.write("**Labels:**")
                                        for label in issue['labels']:
                                            st.badge(label)
                                    st.link_button("View on GitHub", issue['url'])
                    
                    # Pull Requests
                    prs = github_data.get('pull_requests', [])
                    if prs:
                        st.subheader(f"🔄 Pull Requests ({len(prs)})")
                        for pr in prs[:10]:
                            with st.expander(f"#{pr['number']}: {pr['title'][:60]}..."):
                                col_a, col_b = st.columns([3, 1])
                                with col_a:
                                    st.write(f"**Created:** {pr['created_at']} by {pr['author']}")
                                    st.write(f"**Status:** {pr['state']}")
                                    st.write(f"**Branch:** {pr['head_branch']} → {pr['base_branch']}")
                                    if pr['body']:
                                        st.write(f"**Description:** {pr['body'][:200]}...")
                                with col_b:
                                    if pr['mergeable'] is not None:
                                        status = "✅ Mergeable" if pr['mergeable'] else "❌ Conflicts"
                                        st.write(f"**Status:** {status}")
                                    st.link_button("View on GitHub", pr['url'])
                        
                        # PR Review Assistant
                        st.markdown("---")
                        st.subheader("🧪 PR Review Assistant")
                        pr_numbers = [str(p['number']) for p in prs]
                        selected_pr = st.selectbox("Select PR to analyze", pr_numbers)
                        if selected_pr and st.button("Analyze PR"):
                            with st.spinner("Analyzing PR changes..."):
                                summary = agent.get_pr_diff_summary(current_repo_url, int(selected_pr))
                            if summary:
                                st.write(f"Changed files: {len(summary.get('changed_files', []))}")
                                st.write(f"Additions: {summary.get('additions', 0)} | Deletions: {summary.get('deletions', 0)}")
                                if summary.get('risk_files'):
                                    st.warning("Potentially risky files:")
                                    for rf in summary['risk_files']:
                                        st.write(f"- {rf}")
        else:
            st.info("Please clone a repository first in the Repository tab")

    with tab3:
        st.header("🔍 Repository Analysis")
        
        if st.session_state.repo_path and st.session_state.repo_data:
            repo_path = st.session_state.repo_path
            
            # Insights section
            with st.expander("📈 Repository insights", expanded=False):
                if st.button("Compute insights"):
                    with st.spinner("Computing insights..."):
                        top_size = agent.get_top_files_by_size(repo_path)
                        top_lines = agent.get_top_code_files_by_lines(repo_path)
                        todos = agent.scan_todos(repo_path)
                    st.session_state['analysis_top_size'] = top_size
                    st.session_state['analysis_top_lines'] = top_lines
                    st.session_state['analysis_todos'] = todos
                    st.success("Insights ready")
                
                top_size = st.session_state.get('analysis_top_size', [])
                top_lines = st.session_state.get('analysis_top_lines', [])
                todos = st.session_state.get('analysis_todos', {})
                
                if top_size:
                    st.subheader("Largest files (by bytes)")
                    for item in top_size:
                        st.write(f"{item['path']} — {item['size_bytes']} bytes")
                if top_lines:
                    st.subheader("Longest code files (by lines)")
                    for item in top_lines:
                        st.write(f"{item['path']} — {item['lines']} lines")
                if todos:
                    st.subheader("TODO/FIXME tracker")
                    for path, lines in list(todos.items())[:50]:
                        with st.expander(path):
                            for l in lines:
                                st.write(l)
            
            # Repo tree (same as Repository tab)
            st.subheader("📁 Repository Tree")
            col_a2, col_b2 = st.columns([1, 3])
            with col_a2:
                depth2 = st.slider("Depth", min_value=1, max_value=8, value=3, key="analysis_tree_depth")
            with col_b2:
                if st.button("Show Tree", key="analysis_show_tree"):
                    with st.spinner("Building repository tree..."):
                        tree_text2 = agent.build_repo_tree(repo_path, max_depth=depth2)
                    st.session_state['analysis_repo_tree_text'] = tree_text2
            if st.session_state.get('analysis_repo_tree_text'):
                st.code(st.session_state['analysis_repo_tree_text'], language="text")

            # File browser
            st.subheader("📁 File Browser")
            
            # Get all files
            all_files = []
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for file in files:
                    if not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, repo_path)
                        all_files.append(rel_path)
            
            # File selection
            selected_file = st.selectbox("Select a file to view:", [""] + sorted(all_files))
            
            if selected_file:
                file_path = os.path.join(repo_path, selected_file)
                
                # File info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**File:** {selected_file}")
                with col2:
                    try:
                        size = os.path.getsize(file_path)
                        st.write(f"**Size:** {size} bytes")
                    except Exception:
                        st.write("**Size:** Unknown")
                with col3:
                    _, ext = os.path.splitext(selected_file)
                    st.write(f"**Type:** {ext or 'No extension'}")
                
                # Code analysis for supported files
                if selected_file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx')):
                    metrics = agent.analyze_code_file(file_path)
                    
                    st.subheader("📊 Code Metrics")
                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                    with metric_col1:
                        st.metric("Lines", metrics['lines'])
                    with metric_col2:
                        st.metric("Functions", metrics['functions'])
                    with metric_col3:
                        st.metric("Classes", metrics['classes'])
                    with metric_col4:
                        st.metric("Imports", metrics['imports'])
                
                # File content
                st.subheader("📄 File Content")
                content = agent.read_file_content(file_path)
                
                # Determine language for syntax highlighting
                lang_map = {
                    '.py': 'python', '.js': 'javascript', '.jsx': 'javascript',
                    '.ts': 'typescript', '.tsx': 'typescript', '.html': 'html',
                    '.css': 'css', '.json': 'json', '.yaml': 'yaml',
                    '.yml': 'yaml', '.md': 'markdown'
                }
                
                lang = lang_map.get(ext, 'text')
                st.code(content, language=lang)

        else:
            st.info("Please clone a repository first in the Repository tab")
    
    with tab4:
        st.header("🔎 Search")
        if not st.session_state.repo_path:
            st.info("Please clone a repository first in the Repository tab")
        else:
            repo_path = st.session_state.repo_path
            mode = st.radio("Search mode", ["Semantic", "Keyword"], index=0 if AI_IMPORTS_AVAILABLE else 1, horizontal=True)
            query = st.text_input("Enter your search query")
            
            if mode == "Semantic" and not AI_IMPORTS_AVAILABLE:
                st.info("Semantic search disabled in FAST mode. Falling back to keyword search.")
                mode = "Keyword"
            
            if mode == "Semantic":
                if st.button("Build/Refresh Index"):
                    with st.spinner("Building semantic index..."):
                        ok = agent.build_semantic_index(repo_path)
                    if ok:
                        st.success("Semantic index ready")
                    else:
                        st.error("Failed to build index (FAST mode or no files)")
                
                if query:
                    if agent.build_semantic_index(repo_path):
                        with st.spinner("Searching..."):
                            results = agent.semantic_search(query, top_k=10)
                        if results:
                            for r in results:
                                with st.expander(f"{os.path.relpath(r['file_path'], repo_path)} @ {r['offset']}  (score: {r.get('score', 0):.3f})"):
                                    st.code(r['text'], language="text")
                        else:
                            st.info("No results found.")
            else:
                if query:
                    with st.spinner("Searching..."):
                        results = agent.keyword_search(repo_path, query)
                    if results:
                        for r in results:
                            with st.expander(f"{os.path.relpath(r['file_path'], repo_path)} @ {r['offset']}"):
                                st.code(r['text'], language="text")
                    else:
                        st.info("No results found.")

    with tab5:
        st.header("💬 AI Assistant Chat")
        
        # Optional file context for suggestions
        file_context = None
        if st.session_state.repo_path:
            with st.expander("Context (optional): File-aware suggestions"):
                repo_path = st.session_state.repo_path
                files = []
                for root, dirs, fs in os.walk(repo_path):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    for f in fs:
                        if not f.startswith('.'):
                            files.append(os.path.relpath(os.path.join(root, f), repo_path))
                selected = st.selectbox("Select a file for context", [""] + sorted(files))
                if selected:
                    file_context = os.path.join(repo_path, selected)
                    if st.button("Generate code suggestions for file"):
                        with st.spinner("Analyzing file for improvements..."):
                            sugg = agent.generate_code_suggestions(file_context)
                        st.markdown(sugg)
        
        # Quick prompt chips
        cols = st.columns(4)
        quick_prompts = [
            "Show repository structure",
            "Suggest improvements to this repo",
            "List top dependencies",
            "Explain main components"
        ]
        for i, qp in enumerate(quick_prompts):
            if cols[i].button(qp):
                st.session_state.chat_history.append({"role": "user", "content": qp})
                context = f"Repository data: {st.session_state.repo_data}" if st.session_state.repo_data else "No repository loaded"
                resp = agent.generate_ai_response(context, qp, st.session_state.repo_data, st.session_state.github_data)
                st.session_state.chat_history.append({"role": "assistant", "content": resp})
                st.rerun()
        
        # Chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"]) 
        
        # Chat input
        user_input = st.chat_input("Ask about the repository, request code suggestions, or get help...")
        
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            context = f"Repository data: {st.session_state.repo_data}" if st.session_state.repo_data else "No repository loaded"
            response = agent.generate_ai_response(context, user_input, st.session_state.repo_data, st.session_state.github_data)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

    with tab6:
        st.header("🛡️ Security (OSV)")
        if not st.session_state.repo_path:
            st.info("Please clone a repository first in the Repository tab")
        else:
            if st.button("Scan dependencies"):
                with st.spinner("Collecting dependencies..."):
                    pkgs = agent.scan_dependencies(st.session_state.repo_path)
                with st.spinner("Querying OSV..."):
                    vulns = agent.query_osv(pkgs)
                st.session_state['security_results'] = vulns
                st.success(f"Scan complete. Found {len(vulns)} vulnerabilities.")
            
            vulns = st.session_state.get('security_results', [])
            if vulns:
                st.subheader("Results")
                for v in vulns[:200]:
                    with st.expander(f"{v.get('id')} - {v.get('summary')}"):
                        st.write(f"Severity: {v.get('severity', 'N/A')}")
                        aliases = v.get('aliases') or []
                        if aliases:
                            st.write(f"Aliases: {', '.join(aliases)}")
                        refs = v.get('references') or []
                        for ref in refs[:5]:
                            url = ref.get('url')
                            if url:
                                st.write(f"- {url}")
            else:
                st.info("Run a scan to see results.")

if __name__ == "__main__":
    main()