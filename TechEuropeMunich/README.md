# TactoLearn: Autonomous Negotiation Intelligence Agent

> **Upload supplier data → AI instantly becomes that company → Start negotiating immediately!**

TactoLearn is a fully autonomous AI-powered negotiation training agent that automatically processes supplier documents using vector database technology and immediately transforms into that company for realistic negotiation training.

## 🎯 Problem & Solution

**Problem:** Procurement teams need realistic negotiation practice but setting up training scenarios is complex and time-consuming.

**Solution:** TactoLearn is fully autonomous - just upload a supplier PDF/CSV and the AI instantly becomes that company. No setup, no manual steps, just immediate negotiation training with realistic supplier behavior based on actual company data.

## ✨ Core Features

### 🤖 **Fully Autonomous Operation**
- Drop any supplier PDF/CSV into the web interface
- AI automatically extracts pricing, terms, company style, products
- Instantly starts acting as that supplier company
- **Zero manual steps** - upload and start negotiating!

### 🌐 **Modern Web Interface**
- Beautiful drag & drop file upload
- Real-time chat with AI supplier
- Clean, responsive design
- Supplier info panel with extracted data
- Status indicators and strategy display

### 🧠 **Vector Database Intelligence**
- ChromaDB + sentence transformers for document understanding
- Contextual retrieval during negotiations
- Learns from conversation history
- Improves responses based on document context

### 💬 **Natural Conversation**
- Chat directly - no commands needed
- AI responds as the actual supplier company
- Uses real pricing, delivery terms, negotiation style from documents
- Realistic business language and behavior

### 📊 **Smart Document Processing**
- **PDF**: Contracts, proposals, company profiles
- **CSV**: Pricing data, product catalogs, historical orders
- **TXT**: Any text-based supplier information
- Automatic extraction of key business data

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
# Using uv (recommended)
uv add chromadb sentence-transformers watchdog fastapi uvicorn jinja2 python-multipart

# OR using pip
pip install chromadb sentence-transformers watchdog fastapi uvicorn jinja2 python-multipart
```

### 2. **Set API Key**
Edit the `.env` file in the project root:
```bash
# Required for AI responses
OPENAI_API_KEY=your_openai_api_key_here

# Optional configuration
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o
MAX_TOKENS=1000
```

### 3. **Start the Web Interface**
Choose one of these methods:

**Option A: Quick Start Script**
```bash
chmod +x start_web.sh
./start_web.sh
```

**Option B: Direct Command**
```bash
uv run python web_server.py
```

**Option C: Terminal/Command Line Interface**
```bash
uv run python autonomous_agent.py
```

### 4. **Access the Web Interface**
Open your browser and go to: **http://localhost:8000**

### 5. **Upload & Negotiate**
1. **Drag & drop** a supplier file (PDF/CSV/TXT) into the upload area
2. **Wait** for AI processing (shows supplier details automatically)
3. **Start chatting** - type any message and the AI responds as that supplier!

## 🌐 Web Interface Guide

### **Main Interface Components**

1. **Upload Section (Left Panel)**
   - Drag & drop area for files
   - Supported formats: PDF, CSV, TXT
   - Shows supplier info after processing
   - Reset session button

2. **Chat Section (Right Panel)**
   - Real-time conversation with AI supplier
   - Message bubbles for user and supplier
   - Strategy indicators for each response
   - Auto-scroll and message history

3. **Status Indicators**
   - 🔴 Red dot: No supplier loaded
   - 🟢 Green dot: Ready to negotiate
   - Processing animations during file upload

### **User Experience Flow**

```
1. Open http://localhost:8000
   ↓
2. Drag supplier_contract.pdf to upload area
   ↓
3. AI processes: "Processing with AI..."
   ↓
4. Shows: "✅ Ready! You are now negotiating with ACME Manufacturing"
   ↓
5. Supplier info appears: Products, prices, style, discounts
   ↓
6. Chat becomes active: "Type your negotiation message..."
   ↓
7. Start conversation: "Hi, what's your best price for 500 units?"
   ↓
8. AI responds as ACME: "For 500 units, I can offer $95 each..."
```

## 📖 Usage Examples

### **Web Interface Example**
1. **Upload**: Drag `Müller_Precision_Tools_GmbH.pdf` to upload area
2. **Processing**: See loading animation and "Processing with AI..."
3. **Ready**: Interface shows supplier details automatically
4. **Chat**: Start typing - no commands needed!

```
👤 You: Hello, we're interested in your precision cutting tools
🏭 Müller Precision Tools: Hello! Thank you for your interest. We specialize in high-precision cutting tools for automotive and aerospace applications. What specific tools are you looking for?

👤 You: We need 200 carbide end mills, what's your pricing?
🏭 Müller Precision Tools: For 200 carbide end mills, our standard pricing is €85 per unit. However, for quantities over 150 units, we can offer a 8% volume discount, bringing the price to €78.20 per unit.
```

### **Command Line Example**
```bash
🤖 TactoLearn - Autonomous Negotiation Agent
📁 Auto-loading supplier data from: Kraus_Automotive_Systems_AG.csv
✅ Loaded data for: Kraus Automotive Systems AG

🎬 You are now negotiating with Kraus Automotive Systems AG
💡 Just type naturally - ask about pricing, products, delivery, discounts, etc.

👤 You: What's your lead time for electronic control units?
🏭 Kraus Automotive Systems AG: Our standard lead time for ECUs is 6-8 weeks for orders up to 500 units. For larger quantities or custom specifications, we typically need 10-12 weeks.
```

## 🏗️ Architecture & Technology

### **System Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Web Interface  │───▶│  Vector DB      │───▶│   AI Agent      │
│                 │    │                 │    │                 │
│ • File Upload   │    │ • ChromaDB      │    │ • Supplier Role │
│ • Real-time Chat│    │ • Embeddings    │    │ • OpenAI/Claude │
│ • Responsive UI │    │ • Context Search│    │ • Real Responses│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Learning Loop   │
                       │                 │
                       │ • Conversation  │
                       │   Storage       │
                       │ • Improvement   │
                       └─────────────────┘
```

### **Technology Stack**
- **Backend**: FastAPI (Python) for REST API
- **Frontend**: Vanilla HTML/CSS/JavaScript with modern design
- **AI**: OpenAI GPT-4o or Anthropic Claude
- **Vector DB**: ChromaDB with sentence-transformers
- **File Processing**: PyMuPDF for PDFs, Pandas for CSV

## 🗂️ File Structure

```
TechEuropeMunich/
├── web_server.py              # Main web server (FastAPI)
├── autonomous_agent.py        # Command-line interface
├── start_web.sh              # Quick start script
├── .env                      # Configuration file
├── web/
│   └── index.html           # Web interface
├── uploads/                  # Auto-created for file uploads
├── vector_db/               # Auto-created for data storage
├── mcp_host/tools/          # Core AI components
└── examples/                # Sample supplier files
```

## 🔧 Configuration Options

### **Environment Variables (.env)**
```env
# Required - Get from OpenAI or Anthropic
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Provider Selection
LLM_PROVIDER=openai              # or 'anthropic'

# Model Configuration
OPENAI_MODEL=gpt-4o              # or gpt-4o-mini for faster responses
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Performance Settings
MAX_TOKENS=1000                  # Response length limit
API_TIMEOUT=30                   # Request timeout in seconds

# Server Settings
HOST=0.0.0.0                     # Server host (default: 0.0.0.0)
PORT=8000                        # Server port (default: 8000)

# Logging
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
```

### **Vector Database Settings**
```python
# Automatic configuration - stored in ./vector_db/
# Uses sentence-transformers: 'all-MiniLM-L6-v2'
# ChromaDB collections: 'supplier_data', 'conversations'
```

## 📊 Supported Document Formats

### **PDF Documents**
✅ Supplier contracts and agreements  
✅ Company profiles and capabilities  
✅ Pricing sheets and catalogs  
✅ Technical specifications  
✅ Proposal documents  

### **CSV Files**
```csv
supplier_name,product_name,price,delivery_time,quality_score
ACME Manufacturing,Industrial Valve,125.50,14,9.2
TechCorp Industries,Pressure Gauge,45.75,7,8.8
Precision Tools Ltd,Control Panel,850.00,21,9.5
```

### **Text Files**
✅ Contract terms and conditions  
✅ Company policies  
✅ Product descriptions  
✅ Historical negotiation notes  
✅ Technical documentation  

## 🎯 Training Benefits

### **For Procurement Teams**
- **Realistic Practice**: AI behaves like actual suppliers based on real data
- **Risk-Free Environment**: Practice without affecting real supplier relationships
- **Immediate Feedback**: Strategy analysis after each response
- **Company-Specific**: Uses your actual supplier documents and pricing
- **Skill Building**: Develop negotiation confidence and techniques

### **For Training Managers**
- **Easy Setup**: No complex configuration or training required
- **Scalable**: Handle multiple trainees simultaneously
- **Measurable**: Track conversation patterns and improvement
- **Cost-Effective**: Reduce need for expensive external training

## 🚀 Different Ways to Use TactoLearn

### **1. Web Interface (Recommended)**
**Best for**: Teams, presentations, ease of use
```bash
./start_web.sh
# Open http://localhost:8000
```

### **2. Command Line Interface**
**Best for**: Individual training, automation
```bash
uv run python autonomous_agent.py
```

### **3. Interactive Chat**
**Best for**: Quick testing, development
```bash
uv run python smart_chat.py
```

## 🔄 Continuous Learning & Improvement

### **How the AI Learns**
1. **Document Analysis**: Extracts company personality and negotiation style
2. **Conversation Storage**: Saves successful negotiation patterns
3. **Context Building**: Builds knowledge base from multiple documents
4. **Response Improvement**: Learns from conversation outcomes

### **Data Storage**
- **Vector Database**: Stores document embeddings in `./vector_db/`
- **Conversation History**: Saves negotiations for pattern analysis
- **Supplier Profiles**: Caches extracted company information
- **Performance Metrics**: Tracks strategy effectiveness

## 🛠️ Troubleshooting

### **Common Issues & Solutions**

**Web server won't start:**
```bash
# Make sure dependencies are installed
uv add fastapi uvicorn

# Check if port 8000 is available
lsof -i :8000

# Kill existing process if needed
kill -9 <PID>
```

**File upload fails:**
- Ensure file is PDF, CSV, or TXT format
- Check file size (large files may take longer to process)
- Verify API key is set in `.env` file

**AI responses are generic:**
- Upload more detailed supplier documents
- Use documents with specific pricing and terms
- Check that LLM API key is working with `uv run python test_llm.py`

**Slow performance:**
- Switch to `gpt-4o-mini` for faster responses
- Reduce `MAX_TOKENS` in `.env` file
- Use smaller document files for testing

### **Testing Your Setup**

**Test LLM Integration:**
```bash
uv run python test_llm.py
```

**Test All Components:**
```bash
uv run python test_agent.py
```

**Check Example Files:**
```bash
ls examples/
# Should show: supplier_data.csv, supplier_contract.txt
```

## 🛡️ Security & Privacy

- **Local Processing**: All data stays on your machine
- **No Data Sharing**: Documents never leave your environment
- **API Security**: Only sends prompts to LLM, not raw documents
- **Temporary Storage**: Upload files can be deleted after processing

## 🚀 Getting Started Checklist

- [ ] Clone/download TactoLearn project
- [ ] Install dependencies: `uv add chromadb sentence-transformers fastapi uvicorn`
- [ ] Set up API key in `.env` file
- [ ] Test with: `uv run python test_llm.py`
- [ ] Start web interface: `./start_web.sh`
- [ ] Open browser to `http://localhost:8000`
- [ ] Upload a supplier document
- [ ] Start your first negotiation!

---

**🎯 Transform your negotiation training from static documents to dynamic AI conversations in under 5 minutes!**

**Need help?** Check the troubleshooting section above or run the test scripts to verify your setup.
