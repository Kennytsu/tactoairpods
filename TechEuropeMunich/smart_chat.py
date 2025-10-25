#!/usr/bin/env python3
"""
Smart Chat Interface for TactoLearn - Natural Supplier Simulation

This provides a simple interface where users can talk directly to an AI supplier
that automatically uses uploaded company data to respond realistically.
"""

import asyncio
import sys
import os
from pathlib import Path
import json

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_host.tools.analyze_supplier import analyze_supplier_tool
from mcp_host.tools.simulate_supplier_response import simulate_supplier_response_tool

class SmartSupplierChat:
    """Smart supplier chat that automatically uses data and responds naturally"""
    
    def __init__(self):
        self.session_context = {}
        self.negotiation_transcript = []
        self.supplier_loaded = False
        self.supplier_name = "Unknown Supplier"
    
    async def auto_load_supplier_data(self):
        """Automatically try to load supplier data from examples folder"""
        examples_dir = project_root / "examples"
        
        # Look for data files in examples folder
        data_files = []
        if examples_dir.exists():
            for file_path in examples_dir.glob("*"):
                if file_path.suffix.lower() in ['.csv', '.pdf', '.txt']:
                    data_files.append(file_path)
        
        if data_files:
            # Use the first data file found
            chosen_file = data_files[0]
            print(f"📁 Auto-loading supplier data from: {chosen_file.name}")
            
            try:
                result = await analyze_supplier_tool(str(chosen_file), self.session_context)
                self.supplier_name = result.get('supplier_name', chosen_file.stem.title())
                self.supplier_loaded = True
                
                print(f"✅ Loaded data for: {self.supplier_name}")
                if result.get('products'):
                    print(f"   Products: {len(result.get('products', []))} items")
                if result.get('prices'):
                    print(f"   Price range: ${min(result.get('prices', [0])):.2f} - ${max(result.get('prices', [0])):.2f}")
                print()
                
                return True
                
            except Exception as e:
                print(f"⚠️ Could not auto-load data: {str(e)}")
                return False
        else:
            print("📁 No supplier data files found in examples/ folder")
            print("   Place your CSV, PDF, or TXT files there for automatic loading")
            print()
            return False
    
    async def load_custom_file(self, file_path: str):
        """Load a specific supplier data file"""
        print(f"📁 Loading supplier data from: {file_path}")
        
        try:
            result = await analyze_supplier_tool(file_path, self.session_context)
            self.supplier_name = result.get('supplier_name', Path(file_path).stem.title())
            self.supplier_loaded = True
            
            print(f"✅ Loaded data for: {self.supplier_name}")
            if result.get('products'):
                print(f"   Products: {len(result.get('products', []))} items")
            if result.get('prices'):
                prices = result.get('prices', [0])
                print(f"   Price range: ${min(prices):.2f} - ${max(prices):.2f}")
            print()
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading file: {str(e)}")
            return False
    
    async def chat_with_supplier(self, message: str):
        """Send a message and get supplier response"""
        if not self.supplier_loaded:
            print("⚠️ No supplier data loaded. Please load data first.")
            return
        
        print(f"👤 You: {message}")
        
        try:
            result = await simulate_supplier_response_tool(
                message, 
                self.session_context,
                self.negotiation_transcript
            )
            
            response = result.get("response", "Sorry, I couldn't generate a response.")
            strategy = result.get("strategy", "unknown")
            confidence = result.get("confidence", 0)
            
            print(f"🏭 {self.supplier_name}: {response}")
            
            # Only show technical info if confidence is low (debugging)
            if confidence < 0.6:
                print(f"   [Strategy: {strategy} | Confidence: {confidence:.1%}]")
            
        except Exception as e:
            print(f"🏭 {self.supplier_name}: I'm having some technical difficulties right now. Could you repeat that?")
            print(f"   [Error: {str(e)}]")
    
    async def start_smart_chat(self):
        """Start the intelligent chat session"""
        print("\n🎯 TactoLearn - Smart Supplier Training")
        print("=" * 50)
        print("Chat directly with an AI supplier based on real company data!")
        print()
        
        # Try to auto-load data
        auto_loaded = await self.auto_load_supplier_data()
        
        if not auto_loaded:
            # Ask user to provide a file
            while not self.supplier_loaded:
                file_path = input("📁 Enter path to supplier data file (or 'quit'): ").strip()
                
                if file_path.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    return
                
                if file_path and Path(file_path).exists():
                    loaded = await self.load_custom_file(file_path)
                    if loaded:
                        break
                else:
                    print("❌ File not found. Please try again.")
        
        # Start conversation
        print(f"🎬 You are now negotiating with {self.supplier_name}")
        print("💡 Just type naturally - ask about pricing, products, delivery, discounts, etc.")
        print("   Type 'quit' to exit")
        print()
        
        while True:
            try:
                # Get user input
                user_input = input("💬 ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"👋 {self.supplier_name}: Thanks for your time! We look forward to working together.")
                    break
                
                elif not user_input:
                    continue
                
                # Handle special commands (hidden)
                elif user_input.lower().startswith('load '):
                    file_path = user_input[5:].strip()
                    await self.load_custom_file(file_path)
                    continue
                
                elif user_input.lower() == 'info':
                    self.show_supplier_info()
                    continue
                
                # Regular conversation
                await self.chat_with_supplier(user_input)
                print()
                
            except KeyboardInterrupt:
                print(f"\n👋 {self.supplier_name}: Thanks for your time!")
                break
            except EOFError:
                print(f"\n👋 {self.supplier_name}: Thanks for your time!")
                break
            except Exception as e:
                print(f"❌ System error: {str(e)}")
    
    def show_supplier_info(self):
        """Show information about the loaded supplier"""
        if not self.supplier_loaded:
            print("⚠️ No supplier data loaded")
            return
        
        supplier_data = self.session_context.get('supplier_data', {})
        print(f"\n📊 {self.supplier_name} - Company Information")
        print("=" * 40)
        
        if supplier_data.get('products'):
            products = supplier_data['products'][:5]  # Show first 5
            print(f"Products: {', '.join(products)}")
            if len(supplier_data['products']) > 5:
                print(f"   (and {len(supplier_data['products']) - 5} more)")
        
        if supplier_data.get('prices'):
            prices = supplier_data['prices']
            print(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
        
        if supplier_data.get('quality_metrics'):
            avg_quality = sum(supplier_data['quality_metrics']) / len(supplier_data['quality_metrics'])
            print(f"Average quality rating: {avg_quality:.1f}/10")
        
        if supplier_data.get('delivery_times'):
            avg_delivery = sum(supplier_data['delivery_times']) / len(supplier_data['delivery_times'])
            print(f"Average delivery time: {avg_delivery:.0f} days")
        
        print()

async def main():
    """Main entry point"""
    chat = SmartSupplierChat()
    await chat.start_smart_chat()

if __name__ == "__main__":
    asyncio.run(main())