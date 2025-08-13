#!/bin/bash

set -e

MODE=${1:-full}
PORT=${2:-8501}
PRELOAD=${3:-}

if [[ "$MODE" == "fast" ]]; then
  export FAST_MODE=1
  MODE_NAME="FAST"
else
  export FAST_MODE=0
  MODE_NAME="FULL"
fi

echo "🚀 Starting MCP Agent - AI Git Assistant..."
echo "📂 Project Directory: $(pwd)"
echo "⚙️ Mode: ${MODE_NAME}   Port: ${PORT}"
[[ "$PRELOAD" == "preload" ]] && echo "📥 Preloading models enabled"

# Check if virtual environment exists
if [ ! -f ".venv/bin/python" ]; then
  echo "❌ Virtual environment not found!"
  echo "🔧 Creating virtual environment..."
  python3 -m venv .venv
  echo "📦 Installing dependencies..."
  .venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
else
  echo "✅ Virtual environment found"
fi

# Optional: preload models
if [[ "$PRELOAD" == "preload" ]]; then
  echo "📥 Preloading models (one-time warmup)..."
  .venv/bin/python preload_models.py || true
fi

echo "🤖 Starting Streamlit application..."
echo "🌐 Application will open at: http://localhost:${PORT}"
echo "🛑 Press Ctrl+C to stop the application"
echo

.venv/bin/python -m streamlit run app.py --server.port=${PORT} --server.headless=true

echo
echo "👋 Application stopped." 