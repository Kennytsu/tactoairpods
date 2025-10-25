#!/usr/bin/env python3
"""
Web Server for TactoLearn Autonomous Agent

This provides a web interface for file upload and chat functionality.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
import json
import shutil
from typing import Dict, Any, List

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
from pydantic import BaseModel

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_host.tools.vector_db import vector_db
from mcp_host.tools.simulate_supplier_response import simulate_supplier_response_tool

app = FastAPI(title="TactoLearn Web Interface")

# Create directories
web_dir = project_root / "web"
web_dir.mkdir(exist_ok=True)
uploads_dir = project_root / "uploads"
uploads_dir.mkdir(exist_ok=True)

# Templates and static files
templates = Jinja2Templates(directory=str(web_dir))

# Global state for the current session
class SessionState:
    def __init__(self):
        self.current_supplier = None
        self.current_supplier_data = {}
        self.negotiation_transcript = []
        self.session_context = {}

session = SessionState()

# Pydantic models for API
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    supplier_name: str
    response: str
    strategy: str

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload and process with AI"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.csv', '.txt')):
            raise HTTPException(status_code=400, detail="Only PDF, CSV, and TXT files are supported")
        
        # Save uploaded file
        file_path = uploads_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process with vector database
        supplier_profile = await vector_db.process_and_store_document(str(file_path))
        
        # Update session state
        session.current_supplier = supplier_profile.get("supplier_name", file.filename.split('.')[0].title())
        session.current_supplier_data = supplier_profile
        session.session_context['supplier_data'] = supplier_profile
        session.negotiation_transcript = []  # Reset conversation
        
        return JSONResponse({
            "success": True,
            "supplier_name": session.current_supplier,
            "supplier_data": {
                "products": supplier_profile.get("products", [])[:5],  # First 5 products
                "price_range": {
                    "min": min(supplier_profile.get("prices", [0])) if supplier_profile.get("prices") else None,
                    "max": max(supplier_profile.get("prices", [0])) if supplier_profile.get("prices") else None
                },
                "negotiation_style": supplier_profile.get("negotiation_style", "collaborative"),
                "volume_discounts": supplier_profile.get("volume_discounts", False)
            }
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.post("/chat", response_model=ChatResponse)
async def chat_with_supplier(message: ChatMessage):
    """Handle chat messages and generate supplier responses"""
    try:
        if not session.current_supplier:
            raise HTTPException(status_code=400, detail="No supplier loaded. Please upload a file first.")
        
        # Get contextual information from vector database
        context = await vector_db.get_contextual_supplier_info(
            message.message, 
            session.current_supplier
        )
        
        # Enhance session context with vector search results
        enhanced_context = session.session_context.copy()
        if context.get("supplier_data"):
            enhanced_context['supplier_data'].update(context["supplier_data"])
        
        # Add relevant document chunks as context
        if context.get("relevant_info"):
            enhanced_context['contextual_info'] = context["relevant_info"]
        
        # Generate response using enhanced context
        result = await simulate_supplier_response_tool(
            message.message,
            enhanced_context,
            session.negotiation_transcript
        )
        
        response_text = result.get("response", "I'm not sure how to respond to that.")
        strategy = result.get("strategy", "unknown")
        
        # Add to transcript
        session.negotiation_transcript.extend([
            {"role": "buyer", "message": message.message},
            {"role": "supplier", "message": response_text}
        ])
        
        # Store conversation in vector database periodically
        if len(session.negotiation_transcript) % 8 == 0:
            try:
                conversation_data = {
                    "messages": session.negotiation_transcript.copy(),
                    "supplier_id": session.current_supplier,
                    "timestamp": datetime.now().isoformat(),
                    "strategies": [strategy],
                    "outcome": "ongoing"
                }
                await vector_db.store_conversation(conversation_data)
            except:
                pass  # Don't break chat for storage errors
        
        return ChatResponse(
            supplier_name=session.current_supplier,
            response=response_text,
            strategy=strategy
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    """Get current session status"""
    return JSONResponse({
        "supplier_loaded": session.current_supplier is not None,
        "supplier_name": session.current_supplier,
        "conversation_length": len(session.negotiation_transcript),
        "supplier_summary": {
            "products": session.current_supplier_data.get("products", [])[:3],
            "negotiation_style": session.current_supplier_data.get("negotiation_style", "unknown"),
            "volume_discounts": session.current_supplier_data.get("volume_discounts", False)
        } if session.current_supplier else None
    })

@app.post("/reset")
async def reset_session():
    """Reset the current session"""
    session.current_supplier = None
    session.current_supplier_data = {}
    session.negotiation_transcript = []
    session.session_context = {}
    
    return JSONResponse({"success": True, "message": "Session reset successfully"})

if __name__ == "__main__":
    print("🚀 Starting TactoLearn Web Interface...")
    print("📁 Upload files and chat at: http://localhost:8000")
    
    uvicorn.run(
        "web_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )