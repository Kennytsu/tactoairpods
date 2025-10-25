#!/usr/bin/env python3
"""
Autonomous TactoLearn Agent - Upload & Negotiate

This is a fully autonomous negotiation agent that:
1. Automatically processes uploaded PDFs/CSVs using vector database
2. Immediately starts acting as that supplier company
3. No manual steps - just upload and start negotiating!
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_host.tools.vector_db import vector_db
from mcp_host.tools.simulate_supplier_response import simulate_supplier_response_tool

class AutoFileProcessor(FileSystemEventHandler):
    """Automatically processes new files dropped into the uploads folder"""
    
    def __init__(self, agent):
        self.agent = agent
    
    def on_created(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix.lower() in ['.pdf', '.csv', '.txt']:
                print(f"\n🔄 New file detected: {file_path.name}")
                print("Processing automatically...")
                asyncio.create_task(self.agent.process_new_file(file_path))

class AutonomousNegotiationAgent:
    """Fully autonomous negotiation agent with auto-processing"""
    
    def __init__(self):
        self.current_supplier = None
        self.current_supplier_data = {}
        self.negotiation_transcript = []
        self.session_context = {}
        
        # Create uploads directory
        self.uploads_dir = project_root / "uploads"
        self.uploads_dir.mkdir(exist_ok=True)
        
        # File watcher for auto-processing
        self.file_observer = None
    
    async def start_autonomous_agent(self):
        """Start the autonomous agent"""
        print("\n🤖 TactoLearn - Autonomous Negotiation Agent")
        print("=" * 55)
        print("🎯 Upload any supplier PDF/CSV and start negotiating immediately!")
        print()
        
        # Check for existing files first
        await self.check_existing_files()
        
        # Start file watcher for new uploads
        self.start_file_watcher()
        
        # If no supplier loaded, wait for file upload
        if not self.current_supplier:
            print("📁 Drag & drop supplier files into the 'uploads/' folder")
            print("   Supported: PDF, CSV, TXT files")
            print("   Or provide a file path manually")
            print()
            
            # Manual file input option
            while not self.current_supplier:
                user_input = input("💬 Upload file path (or just chat if supplier loaded): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if user_input and Path(user_input).exists():
                    await self.process_new_file(Path(user_input))
                    break
                elif user_input:
                    print("❌ File not found. Try again or drop file in uploads/ folder")
        
        # Start negotiation chat
        if self.current_supplier:
            await self.start_negotiation_chat()
    
    async def check_existing_files(self):
        """Check for existing files in uploads directory"""
        existing_files = list(self.uploads_dir.glob("*"))
        pdf_csv_files = [f for f in existing_files if f.suffix.lower() in ['.pdf', '.csv', '.txt']]
        
        if pdf_csv_files:
            print(f"📂 Found {len(pdf_csv_files)} file(s) in uploads directory")
            
            # Process the most recent file
            latest_file = max(pdf_csv_files, key=lambda f: f.stat().st_mtime)
            print(f"🔄 Auto-processing latest file: {latest_file.name}")
            await self.process_new_file(latest_file)
    
    def start_file_watcher(self):
        """Start watching uploads directory for new files"""
        event_handler = AutoFileProcessor(self)
        self.file_observer = Observer()
        self.file_observer.schedule(event_handler, str(self.uploads_dir), recursive=False)
        self.file_observer.start()
        print(f"👁️  Watching {self.uploads_dir} for new files...")
    
    async def process_new_file(self, file_path: Path):
        """Process a new supplier file automatically"""
        try:
            print(f"🧠 Processing {file_path.name} with AI...")
            print("   Extracting supplier data, pricing, terms, etc.")
            
            # Process with vector database
            supplier_profile = await vector_db.process_and_store_document(str(file_path))
            
            # Update current supplier
            self.current_supplier = supplier_profile.get("supplier_name", file_path.stem.title())
            self.current_supplier_data = supplier_profile
            
            # Update session context for compatibility
            self.session_context['supplier_data'] = supplier_profile
            
            # Clear previous conversation
            self.negotiation_transcript = []
            
            print(f"✅ Ready! You are now negotiating with {self.current_supplier}")
            
            # Show supplier summary
            self.show_supplier_summary()
            
            print("💡 Start typing to begin negotiation - the AI will respond as this company!")
            print()
            
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {str(e)}")
    
    def show_supplier_summary(self):
        """Show a quick summary of the loaded supplier"""
        data = self.current_supplier_data
        
        print(f"\n📊 {self.current_supplier} - Quick Summary")
        print("─" * 40)
        
        if data.get('products'):
            products = data['products'][:3]
            print(f"🔧 Products: {', '.join(products)}")
            if len(data['products']) > 3:
                print(f"   (and {len(data['products']) - 3} more...)")
        
        if data.get('prices'):
            prices = data['prices']
            print(f"💰 Price range: ${min(prices):.2f} - ${max(prices):.2f}")
        
        if data.get('negotiation_style'):
            print(f"🎯 Style: {data['negotiation_style'].title()}")
        
        if data.get('volume_discounts'):
            print(f"📦 Volume discounts: {'✅ Available' if data['volume_discounts'] else '❌ Not offered'}")
        
        print()
    
    async def start_negotiation_chat(self):
        """Start the natural negotiation conversation"""
        print(f"🎬 Negotiation with {self.current_supplier} - LIVE")
        print("─" * 50)
        print(f"🏭 {self.current_supplier}: Hello! Thanks for reaching out. How can we help you today?")
        print()
        
        while True:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    await self.end_negotiation()
                    break
                
                elif user_input.lower() == 'summary':
                    self.show_supplier_summary()
                    continue
                
                elif user_input.lower().startswith('upload '):
                    file_path = user_input[7:].strip()
                    if Path(file_path).exists():
                        await self.process_new_file(Path(file_path))
                    else:
                        print("❌ File not found")
                    continue
                
                elif not user_input:
                    continue
                
                # Generate supplier response using vector database context
                await self.generate_contextual_response(user_input)
                print()
                
            except KeyboardInterrupt:
                await self.end_negotiation()
                break
            except EOFError:
                await self.end_negotiation()
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    async def generate_contextual_response(self, user_message: str):
        """Generate intelligent supplier response using vector database"""
        try:
            # Get contextual information from vector database
            context = await vector_db.get_contextual_supplier_info(
                user_message, 
                self.current_supplier
            )
            
            # Enhance session context with vector search results
            enhanced_context = self.session_context.copy()
            if context.get("supplier_data"):
                enhanced_context['supplier_data'].update(context["supplier_data"])
            
            # Add relevant document chunks as context
            if context.get("relevant_info"):
                enhanced_context['contextual_info'] = context["relevant_info"]
            
            # Generate response using enhanced context
            result = await simulate_supplier_response_tool(
                user_message,
                enhanced_context,
                self.negotiation_transcript
            )
            
            response = result.get("response", "I'm not sure how to respond to that.")
            strategy = result.get("strategy", "unknown")
            confidence = result.get("confidence", 0)
            
            # Enhanced confidence with vector database context
            vector_confidence = context.get("confidence", 0)
            combined_confidence = (confidence + vector_confidence) / 2
            
            print(f"🏭 {self.current_supplier}: {response}")
            
            # Show debug info for low confidence
            if combined_confidence < 0.5:
                print(f"   [Strategy: {strategy} | Confidence: {combined_confidence:.1%} | Context: {len(context.get('relevant_info', []))} chunks]")
            
            # Store conversation in vector database for learning
            await self.store_conversation_turn(user_message, response, strategy)
            
        except Exception as e:
            print(f"🏭 {self.current_supplier}: I'm having some technical difficulties. Could you repeat that?")
            print(f"   [Error: {str(e)}]")
    
    async def store_conversation_turn(self, user_message: str, supplier_response: str, strategy: str):
        """Store conversation turn for learning"""
        try:
            # Add to transcript
            self.negotiation_transcript.extend([
                {"role": "buyer", "message": user_message},
                {"role": "supplier", "message": supplier_response}
            ])
            
            # Store in vector database periodically (every 4 messages)
            if len(self.negotiation_transcript) % 8 == 0:  # Every 4 exchanges
                conversation_data = {
                    "messages": self.negotiation_transcript.copy(),
                    "supplier_id": self.current_supplier,
                    "timestamp": datetime.now().isoformat(),
                    "strategies": [strategy],
                    "outcome": "ongoing"
                }
                
                await vector_db.store_conversation(conversation_data)
            
        except Exception as e:
            # Don't break the flow for storage errors
            pass
    
    async def end_negotiation(self):
        """End the negotiation gracefully"""
        print(f"\n🏭 {self.current_supplier}: Thank you for your time! We look forward to working together.")
        
        # Store final conversation
        if self.negotiation_transcript:
            try:
                conversation_data = {
                    "messages": self.negotiation_transcript,
                    "supplier_id": self.current_supplier,
                    "timestamp": datetime.now().isoformat(),
                    "outcome": "completed"
                }
                await vector_db.store_conversation(conversation_data)
                print("💾 Conversation saved for future training improvements")
            except:
                pass
        
        # Stop file watcher
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
        
        print("👋 Thanks for using TactoLearn!")

def create_sample_upload():
    """Create a sample file in uploads directory if none exists"""
    uploads_dir = project_root / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    
    sample_files = list(uploads_dir.glob("*"))
    if not sample_files:
        # Copy example file to uploads
        example_file = project_root / "examples" / "supplier_data.csv"
        if example_file.exists():
            shutil.copy(example_file, uploads_dir / "sample_supplier.csv")
            print(f"📄 Created sample file: {uploads_dir}/sample_supplier.csv")

async def main():
    """Main entry point for autonomous agent"""
    print("🚀 Initializing TactoLearn Autonomous Agent...")
    
    # Create sample upload if needed
    create_sample_upload()
    
    # Start the agent
    agent = AutonomousNegotiationAgent()
    await agent.start_autonomous_agent()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user")
    except Exception as e:
        print(f"\n❌ Agent error: {str(e)}")
        import traceback
        traceback.print_exc()