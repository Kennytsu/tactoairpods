#!/usr/bin/env python3
"""
Simple Chat Interface for TactoLearn Negotiation Intelligence Agent

This provides a straightforward chat interface for testing the agent.
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

async def main():
    """Simple chat interface"""
    print("\n🎯 TactoLearn Negotiation Intelligence Agent")
    print("=" * 50)
    print("Welcome to your AI-powered negotiation training!")
    print()
    
    # Initialize session
    session_context = {}
    negotiation_transcript = []
    supplier_data_loaded = False
    
    print("Let's start by loading some supplier data...")
    
    # Load sample data
    sample_file = project_root / "examples" / "supplier_data.csv"
    if sample_file.exists():
        print(f"📊 Loading supplier data from: {sample_file}")
        try:
            result = await analyze_supplier_tool(str(sample_file), session_context)
            print("✅ Supplier data loaded successfully!")
            print(f"   Supplier: {result.get('supplier_name', 'Unknown')}")
            print(f"   Products: {len(result.get('products', []))} found")
            print(f"   Prices: {len(result.get('prices', []))} price points")
            supplier_data_loaded = True
        except Exception as e:
            print(f"❌ Error loading supplier data: {str(e)}")
            return
    else:
        print("❌ Sample data file not found. Please provide a supplier data file.")
        return
    
    print("\n🎬 Starting negotiation simulation...")
    print("You are now negotiating with ACME Manufacturing!")
    print("Try asking about pricing, discounts, delivery times, etc.")
    print("Type 'quit' to exit, 'summary' to analyze, 'feedback' for training tips")
    print()
    
    while True:
        try:
            # Get user input
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! Keep practicing your negotiation skills!")
                break
            
            elif user_input.lower() == 'summary':
                print("📊 Analyzing conversation...")
                try:
                    result = await summarize_negotiation_transcript_tool("", negotiation_transcript)
                    print("✅ Analysis completed!")
                    
                    summary = result.get("summary", {})
                    sentiment = result.get("sentiment_analysis", {})
                    
                    print(f"   Messages exchanged: {summary.get('total_messages', 0)}")
                    print(f"   Your sentiment: {sentiment.get('buyer_sentiment', {}).get('label', 'unknown')}")
                    print(f"   Supplier sentiment: {sentiment.get('supplier_sentiment', {}).get('label', 'unknown')}")
                except Exception as e:
                    print(f"❌ Error analyzing conversation: {str(e)}")
                continue
            
            elif user_input.lower() == 'feedback':
                print("🎓 Generating training feedback...")
                try:
                    analysis_result = await summarize_negotiation_transcript_tool("", negotiation_transcript)
                    feedback_result = await generate_feedback_tool(analysis_result)
                    print("✅ Feedback generated!")
                    print("\n" + "="*60)
                    print(feedback_result)
                    print("="*60)
                except Exception as e:
                    print(f"❌ Error generating feedback: {str(e)}")
                continue
            
            elif not user_input:
                continue
            
            # Generate supplier response
            print("🤖 Generating supplier response...")
            try:
                result = await simulate_supplier_response_tool(
                    user_input, 
                    session_context,
                    negotiation_transcript
                )
                
                response = result.get("response", "No response generated")
                strategy = result.get("strategy", "unknown")
                confidence = result.get("confidence", 0)
                
                print(f"🏭 Supplier: {response}")
                print(f"   Strategy: {strategy} | Confidence: {confidence:.1%}")
                
            except Exception as e:
                print(f"❌ Error generating response: {str(e)}")
            
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye! Keep practicing your negotiation skills!")
            break
        except EOFError:
            print("\nGoodbye! Keep practicing your negotiation skills!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            break

if __name__ == "__main__":
    asyncio.run(main())




