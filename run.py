#!/usr/bin/env python3
"""
Simple runner script for MCP Agent
"""
import subprocess
import sys
import os

def main():
    """Run the MCP Agent Streamlit application"""
    print("🤖 Starting MCP Agent - AI Git Assistant...")
    print("📂 Current directory:", os.getcwd())
    
    try:
        # Run Streamlit app
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port=8501"]
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 MCP Agent stopped by user")
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install requirements:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error running MCP Agent: {e}")

if __name__ == "__main__":
    main() 