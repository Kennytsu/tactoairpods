#!/usr/bin/env python3
"""
Test script for TactoLearn Negotiation Intelligence Agent

This script tests the basic functionality of the MCP tools.
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

async def test_analyze_supplier():
    """Test the analyze_supplier tool"""
    print("🧪 Testing analyze_supplier tool...")
    
    # Test with CSV file
    csv_file = project_root / "examples" / "supplier_data.csv"
    if csv_file.exists():
        session_context = {}
        result = await analyze_supplier_tool(str(csv_file), session_context)
        print(f"✅ CSV analysis successful: {len(result.get('products', []))} products found")
        print(f"   Supplier: {result.get('supplier_name', 'Unknown')}")
        print(f"   Prices: {len(result.get('prices', []))} price points")
    else:
        print("❌ CSV test file not found")
    
    # Test with TXT file (simulating PDF)
    txt_file = project_root / "examples" / "supplier_contract.txt"
    if txt_file.exists():
        session_context = {}
        result = await analyze_supplier_tool(str(txt_file), session_context)
        print(f"✅ TXT analysis successful: {result.get('text_length', 0)} characters processed")
        print(f"   Supplier: {result.get('supplier_name', 'Unknown')}")
    else:
        print("❌ TXT test file not found")

async def test_simulate_response():
    """Test the simulate_supplier_response tool"""
    print("\n🧪 Testing simulate_supplier_response tool...")
    
    # Create mock session context
    session_context = {
        'supplier_data': {
            'supplier_name': 'ACME Manufacturing',
            'products': ['Industrial Valves', 'Pressure Gauges'],
            'prices': [125.50, 45.75],
            'quality_metrics': [8.5, 9.2]
        }
    }
    
    negotiation_transcript = []
    
    # Test different types of messages
    test_messages = [
        "Hello, we're interested in discussing pricing",
        "We'd like a 10% discount for our next order",
        "What's your best price for 1000 units?",
        "We're considering other suppliers"
    ]
    
    for message in test_messages:
        result = await simulate_supplier_response_tool(
            message, 
            session_context, 
            negotiation_transcript
        )
        print(f"✅ Response generated for: '{message[:30]}...'")
        print(f"   Strategy: {result.get('strategy', 'unknown')}")
        print(f"   Confidence: {result.get('confidence', 0):.1%}")

async def test_summarize_transcript():
    """Test the summarize_negotiation_transcript tool"""
    print("\n🧪 Testing summarize_negotiation_transcript tool...")
    
    # Create mock transcript
    mock_transcript = [
        {"role": "buyer", "message": "We'd like to discuss pricing for our next order"},
        {"role": "supplier", "message": "Thank you for reaching out. We're pleased to discuss your requirements"},
        {"role": "buyer", "message": "What kind of volume discount can you offer for 1000 units?"},
        {"role": "supplier", "message": "We're open to discussing pricing options. What timeline are you working with?"},
        {"role": "buyer", "message": "We need delivery by next month"},
        {"role": "supplier", "message": "Given the timeline, we can expedite delivery with priority handling"}
    ]
    
    result = await summarize_negotiation_transcript_tool("", mock_transcript)
    print(f"✅ Transcript analysis successful")
    print(f"   Total messages: {result.get('summary', {}).get('total_messages', 0)}")
    print(f"   Buyer sentiment: {result.get('sentiment_analysis', {}).get('buyer_sentiment', {}).get('label', 'unknown')}")
    print(f"   Strategies used: {len(result.get('strategy_analysis', {}).get('buyer_strategies', []))}")

async def test_generate_feedback():
    """Test the generate_feedback tool"""
    print("\n🧪 Testing generate_feedback tool...")
    
    # Create mock report data
    mock_report = {
        "summary": {
            "total_messages": 6,
            "buyer_messages": 3,
            "supplier_messages": 3,
            "conversation_balance": 1.0
        },
        "sentiment_analysis": {
            "buyer_sentiment": {"score": 0.1, "label": "positive", "confidence": 0.7},
            "supplier_sentiment": {"score": 0.2, "label": "positive", "confidence": 0.8},
            "overall_sentiment": {"score": 0.15, "label": "positive", "confidence": 0.75}
        },
        "strategy_analysis": {
            "buyer_strategies": ["price_focus", "volume_leverage"],
            "supplier_strategies": ["value_proposition", "relationship_focus"],
            "strategy_effectiveness": {
                "buyer_strategy_count": 2,
                "supplier_strategy_count": 2,
                "strategy_diversity": 4,
                "balanced_negotiation": True
            }
        },
        "improvement_areas": [
            "Consider using competition leverage more effectively",
            "Ask for specific discount percentages"
        ],
        "strengths": [
            "Maintained professional tone throughout",
            "Used volume as leverage effectively"
        ]
    }
    
    result = await generate_feedback_tool(mock_report)
    print(f"✅ Feedback generation successful")
    print(f"   Feedback length: {len(result)} characters")
    print(f"   Contains executive summary: {'Executive Summary' in result}")
    print(f"   Contains recommendations: {'Recommendations' in result}")

async def main():
    """Run all tests"""
    print("🎯 TactoLearn Negotiation Intelligence Agent - Test Suite")
    print("=" * 60)
    
    try:
        await test_analyze_supplier()
        await test_simulate_response()
        await test_summarize_transcript()
        await test_generate_feedback()
        
        print("\n🎉 All tests completed successfully!")
        print("The TactoLearn Negotiation Intelligence Agent is ready to use.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
