#!/bin/bash
set -e

echo "🚀 Starting Pendo Data Generation API..."
echo "Environment variables:"
echo "  PORT: $PORT"
echo "  PYTHONPATH: $PYTHONPATH"
echo "  PWD: $(pwd)"

echo "📁 Directory contents:"
ls -la

echo "🐍 Python version:"
python --version

echo "📦 Checking Python imports..."
python -c "from backend.main import app; print('✅ FastAPI app imported successfully')"

echo "🎭 Checking Playwright..."
python -c "import playwright; print('✅ Playwright imported successfully')"

echo "🌐 Starting uvicorn server..."
echo "Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT --log-level debug --access-log"

exec uvicorn backend.main:app --host 0.0.0.0 --port $PORT --log-level debug --access-log 