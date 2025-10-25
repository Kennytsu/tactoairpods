#!/usr/bin/env python3
"""
Direct Chat Interface for TactoLearn Negotiation Intelligence Agent

This provides a simple chat interface without the complex MCP setup.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_host.tools.analyze_supplier import analyze_supplier_tool
from mcp_host.tools.simulate_supplier_response import simulate_supplier_response_tool
from mcp_host.tools.summarize_negotiation_transcript import summarize_negotiation_transcript_tool
from mcp_host.tools.generate_feedback import generate_feedback_tool

class NegotiationChat:
    """Simple chat interface for negotiation training"""
    
    def __init__(self):
        self.session_context = {}
        self.negotiation_transcript = []
        self.supplier_data_loaded = False
    
    async def start_chat(self):
        """Start the interactive chat session"""
        print("\n🎯 TactoLearn Negotiation Intelligence Agent")
        print("=" * 50)
        print("Welcome to your AI-powered negotiation training session!")
        print("Type 'help' for available commands, 'quit' to exit.")
        print()
        
        while True:
            try:
                command = input("Negotiation Trainer> ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! Keep practicing your negotiation skills!")
                    break
                
                elif command.lower() == 'help':
                    self.print_help()
                
                elif command.startswith('analyze '):
                    file_path = command[8:].strip()
                    if file_path:
                        await self.analyze_supplier(file_path)
                    else:
                        print("Please provide a file path: analyze <file_path>")
                
                elif command.startswith('negotiate '):
                    message = command[10:].strip()
                    if message:
                        await self.negotiate(message)
                    else:
                        print("Please provide a message: negotiate <your_message>")
                
                elif command.lower() == 'summarize':
                    await self.summarize_conversation()
                
                elif command.lower() == 'feedback':
                    await self.get_feedback()
                
                elif command.lower() == 'demo':
                    await self.run_demo()
                
                elif command.lower() == 'status':
                    self.show_status()
                
                else:
                    print("Unknown command. Type 'help' for available commands.")
                
                print()  # Add spacing between commands
                
            except KeyboardInterrupt:
                print("\nGoodbye! Keep practicing your negotiation skills!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
    
    async def analyze_supplier(self, file_path: str):
        """Analyze supplier data from a file"""
        print(f"🔍 Analyzing supplier data from: {file_path}")
        
        try:
            result = await analyze_supplier_tool(file_path, self.session_context)
            
            print("✅ Analysis completed successfully!")
            print(f"   Supplier: {result.get('supplier_name', 'Unknown')}")
            print(f"   Products: {len(result.get('products', []))} found")
            print(f"   Prices: {len(result.get('prices', []))} price points")
            print(f"   Quality metrics: {len(result.get('quality_metrics', []))} scores")
            
            self.supplier_data_loaded = True
            
        except Exception as e:
            print(f"❌ Error analyzing supplier file: {str(e)}")
    
    async def negotiate(self, message: str):
        """Send a negotiation message"""
        if not self.supplier_data_loaded:
            print("⚠️  No supplier data loaded. Please run 'analyze <file_path>' first.")
            print("   Example: analyze examples/supplier_data.csv")
            return
        
        print(f"👤 You: {message}")
        
        try:
            result = await simulate_supplier_response_tool(
                message, 
                self.session_context,
                self.negotiation_transcript
            )
            
            response = result.get("response", "No response generated")
            strategy = result.get("strategy", "unknown")
            confidence = result.get("confidence", 0)
            
            print(f"🏭 Supplier: {response}")
            print(f"   Strategy: {strategy} | Confidence: {confidence:.1%}")
            
        except Exception as e:
            print(f"❌ Error generating supplier response: {str(e)}")
    
    async def summarize_conversation(self):
        """Analyze the current conversation"""
        if not self.negotiation_transcript:
            print("⚠️  No conversation to analyze. Start negotiating first!")
            return
        
        print("📊 Analyzing conversation...")
        
        try:
            result = await summarize_negotiation_transcript_tool("", self.negotiation_transcript)
            
            print("✅ Conversation analysis completed!")
            
            summary = result.get("summary", {})
            sentiment = result.get("sentiment_analysis", {})
            strategies = result.get("strategy_analysis", {})
            
            print(f"   Total messages: {summary.get('total_messages', 0)}")
            print(f"   Buyer messages: {summary.get('buyer_messages', 0)}")
            print(f"   Supplier messages: {summary.get('supplier_messages', 0)}")
            
            buyer_sentiment = sentiment.get("buyer_sentiment", {})
            supplier_sentiment = sentiment.get("supplier_sentiment", {})
            
            print(f"   Your sentiment: {buyer_sentiment.get('label', 'unknown')}")
            print(f"   Supplier sentiment: {supplier_sentiment.get('label', 'unknown')}")
            
            buyer_strategies = strategies.get("buyer_strategies", [])
            print(f"   Your strategies: {', '.join(buyer_strategies) if buyer_strategies else 'None detected'}")
            
        except Exception as e:
            print(f"❌ Error analyzing conversation: {str(e)}")
    
    async def get_feedback(self):
        """Generate training feedback"""
        if not self.negotiation_transcript:
            print("⚠️  No conversation to analyze. Start negotiating first!")
            return
        
        print("🎓 Generating training feedback...")
        
        try:
            # First get the analysis
            analysis_result = await summarize_negotiation_transcript_tool("", self.negotiation_transcript)
            
            # Generate feedback
            feedback_result = await generate_feedback_tool(analysis_result)
            
            print("✅ Feedback generated!")
            print("\n" + "="*60)
            print(feedback_result)
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error generating feedback: {str(e)}")
    
    async def run_demo(self):
        """Run a demonstration negotiation"""
        print("\n🎬 Running Demo Negotiation")
        print("=" * 30)
        
        # Load sample data first
        sample_file = project_root / "examples" / "supplier_data.csv"
        if sample_file.exists():
            await self.analyze_supplier(str(sample_file))
        else:
            print("❌ Sample data file not found. Please provide a supplier data file.")
            return
        
        # Demo messages
        demo_messages = [
            "Hello, we're interested in discussing pricing for our upcoming order",
            "We're looking at ordering 1000 units for next quarter",
            "What kind of volume discount can you offer for this quantity?",
            "Our budget is tight this quarter, can you work with us on pricing?",
            "We've been a loyal customer for 2 years, is there any flexibility?"
        ]
        
        print("Starting demo negotiation...")
        print()
        
        for i, message in enumerate(demo_messages, 1):
            print(f"[Message {i}]")
            await self.negotiate(message)
            print()
            
            # Small delay for realism
            await asyncio.sleep(1)
        
        print("Demo negotiation completed!")
        print("Now analyzing the conversation...")
        await self.summarize_conversation()
        
        print("\nGenerating feedback...")
        await self.get_feedback()
    
    def show_status(self):
        """Show current session status"""
        print("\n📊 Session Status")
        print("=" * 20)
        print(f"Supplier data loaded: {'✅ Yes' if self.supplier_data_loaded else '❌ No'}")
        print(f"Conversation messages: {len(self.negotiation_transcript)}")
        
        if self.supplier_data_loaded:
            supplier_data = self.session_context.get('supplier_data', {})
            print(f"Supplier: {supplier_data.get('supplier_name', 'Unknown')}")
            print(f"Products: {len(supplier_data.get('products', []))}")
            print(f"Prices: {len(supplier_data.get('prices', []))}")
    
    def print_help(self):
        """Print help information"""
        print("""
Available Commands:
==================

analyze <file_path>     - Analyze supplier data from CSV, PDF, or TXT file
negotiate <message>     - Send a negotiation message to the supplier
summarize              - Analyze the current negotiation conversation
feedback               - Generate training feedback and recommendations
demo                   - Run a demonstration negotiation
status                 - Show current session status
help                   - Show this help message
quit/exit/q            - Exit the application

Example Usage:
=============
1. analyze examples/supplier_data.csv
2. negotiate "We'd like to discuss pricing for our next quarter order"
3. negotiate "What kind of volume discount can you offer?"
4. summarize
5. feedback

Tips:
=====
- Start by analyzing supplier data to load context
- Use specific, business-like language in negotiations
- Ask for discounts, volume pricing, delivery terms
- Mention competitors, long-term relationships, or urgency
- Get feedback after each negotiation session
""")

async def main():
    """Main entry point"""
    chat = NegotiationChat()
    await chat.start_chat()

if __name__ == "__main__":
    asyncio.run(main())




