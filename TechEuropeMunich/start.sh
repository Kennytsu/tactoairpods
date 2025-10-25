#!/bin/bash
# TactoLearn Negotiation Intelligence Agent - Startup Script

echo "🎯 TactoLearn Negotiation Intelligence Agent"
echo "============================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import mcp, pandas, fitz" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    uv add mcp pandas PyMuPDF python-dotenv aiofiles
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting TactoLearn Negotiation Intelligence Agent..."
echo ""
echo "Available commands:"
echo "  analyze <file_path>     - Analyze supplier data from CSV or PDF"
echo "  negotiate <message>    - Send a negotiation message to the supplier"
echo "  summarize             - Analyze the current negotiation transcript"
echo "  feedback              - Generate training feedback and recommendations"
echo "  demo                  - Run a demonstration negotiation"
echo "  help                  - Show help information"
echo "  quit                  - Exit the application"
echo ""

# Start the client
python mcp_client/client.py mcp_host/host.py



