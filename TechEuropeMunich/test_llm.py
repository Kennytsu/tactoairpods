#!/usr/bin/env python3
"""
Test script for LLM integration in TactoLearn Negotiation Intelligence Agent

This script tests the LLM-powered functionality.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_host.tools.llm_service import llm_service

async def test_llm_service():
    """Test the LLM service functionality"""
    print("🤖 Testing LLM Service Integration")
    print("=" * 40)
    
    # Check if API keys are configured
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key and not anthropic_key:
        print("❌ No API keys found in environment variables")
        print("Please add your API key to the .env file:")
        print("OPENAI_API_KEY=your_key_here")
        print("or")
        print("ANTHROPIC_API_KEY=your_key_here")
        return False
    
    print(f"✅ API keys found")
    print(f"Provider: {llm_service.provider}")
    print(f"Model: {llm_service.model}")
    
    # Test supplier response generation
    print("\n🧪 Testing supplier response generation...")
    
    supplier_data = {
        "supplier_name": "ACME Manufacturing",
        "products": ["Industrial Valves", "Pressure Gauges"],
        "prices": [125.50, 45.75],
        "quality_metrics": [8.5, 9.2],
        "delivery_times": [14, 10]
    }
    
    conversation_history = [
        {"role": "buyer", "message": "Hello, we're interested in discussing pricing"},
        {"role": "supplier", "message": "Thank you for reaching out. We're pleased to discuss your requirements."}
    ]
    
    try:
        response = await llm_service.generate_supplier_response(
            "We'd like a 10% discount for our next order of 1000 units",
            supplier_data,
            conversation_history,
            "collaborative"
        )
        
        print("✅ LLM response generated successfully!")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"❌ Error generating LLM response: {str(e)}")
        return False
    
    # Test sentiment analysis
    print("\n🧪 Testing sentiment analysis...")
    
    test_messages = [
        {"role": "buyer", "message": "We're very interested in your products and would like to discuss pricing"},
        {"role": "supplier", "message": "Thank you for your interest. We're pleased to work with you on this opportunity"},
        {"role": "buyer", "message": "What kind of volume discount can you offer?"},
        {"role": "supplier", "message": "We're open to discussing pricing options. What timeline are you working with?"}
    ]
    
    try:
        sentiment_result = await llm_service.analyze_conversation_sentiment(test_messages)
        
        print("✅ Sentiment analysis completed successfully!")
        print(f"Buyer sentiment: {sentiment_result.get('buyer_sentiment', 'unknown')}")
        print(f"Supplier sentiment: {sentiment_result.get('supplier_sentiment', 'unknown')}")
        print(f"Overall tone: {sentiment_result.get('overall_tone', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Error analyzing sentiment: {str(e)}")
        return False
    
    # Test feedback generation
    print("\n🧪 Testing feedback generation...")
    
    mock_analysis = {
        "summary": {
            "total_messages": 4,
            "buyer_messages": 2,
            "supplier_messages": 2
        },
        "sentiment_analysis": {
            "buyer_sentiment": "positive",
            "supplier_sentiment": "positive",
            "overall_tone": "collaborative"
        },
        "strategy_analysis": {
            "buyer_strategies": ["price_focus", "volume_leverage"],
            "supplier_strategies": ["value_proposition", "relationship_focus"]
        }
    }
    
    try:
        feedback = await llm_service.generate_training_feedback(
            mock_analysis,
            test_messages
        )
        
        print("✅ Feedback generation completed successfully!")
        print(f"Feedback length: {len(feedback)} characters")
        print(f"Preview: {feedback[:200]}...")
        
    except Exception as e:
        print(f"❌ Error generating feedback: {str(e)}")
        return False
    
    print("\n🎉 All LLM tests passed!")
    print("Your TactoLearn agent is now powered by AI!")
    
    return True

async def main():
    """Main test function"""
    print("🎯 TactoLearn LLM Integration Test")
    print("=" * 50)
    
    try:
        success = await test_llm_service()
        
        if success:
            print("\n✅ LLM integration is working correctly!")
            print("You can now use the agent with real AI-powered responses.")
        else:
            print("\n❌ LLM integration test failed.")
            print("Please check your API key configuration.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
