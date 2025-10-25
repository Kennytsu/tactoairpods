#!/bin/bash

# TactoLearn Web Interface Launcher
echo "🚀 Starting TactoLearn Web Interface..."
echo "📁 Upload files and chat at: http://localhost:8000"
echo ""

# Start the web server using uv
uv run python web_server.py