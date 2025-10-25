"""
Summarize Negotiation Transcript Tool

This module provides functionality to analyze negotiation transcripts
and extract key metrics, sentiment, and strategy patterns using LLM integration.
"""

import os
import json
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter

from .llm_service import llm_service

logger = logging.getLogger(__name__)

async def summarize_negotiation_transcript_tool(
    transcript_path: str,
    negotiation_transcript: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Analyze a negotiation transcript to extract key metrics and patterns.
    
    Args:
        transcript_path: Path to the negotiation transcript file (optional)
        negotiation_transcript: In-memory transcript data
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Use in-memory transcript if available, otherwise read from file
        if negotiation_transcript:
            transcript_data = negotiation_transcript
        elif transcript_path and os.path.exists(transcript_path):
            transcript_data = await _read_transcript_file(transcript_path)
        else:
            raise ValueError("No transcript data available")
        
        if not transcript_data:
            raise ValueError("Empty transcript data")
        
        # Perform comprehensive analysis
        analysis_result = await _analyze_transcript(transcript_data)
        
        logger.info(f"Successfully analyzed negotiation transcript with {len(transcript_data)} messages")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error analyzing transcript: {str(e)}")
        raise

async def _read_transcript_file(transcript_path: str) -> List[Dict[str, str]]:
    """Read transcript from file"""
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse as JSON first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Parse as plain text
            return _parse_text_transcript(content)
            
    except Exception as e:
        logger.error(f"Error reading transcript file {transcript_path}: {str(e)}")
        raise

def _parse_text_transcript(content: str) -> List[Dict[str, str]]:
    """Parse plain text transcript into structured format"""
    lines = content.strip().split('\n')
    transcript = []
    
    current_role = None
    current_message = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for role indicators
        if line.lower().startswith(('buyer:', 'user:', 'customer:')):
            if current_role and current_message:
                transcript.append({
                    "role": current_role,
                    "message": ' '.join(current_message)
                })
            current_role = "buyer"
            current_message = [line.split(':', 1)[1].strip()]
        elif line.lower().startswith(('supplier:', 'seller:', 'vendor:')):
            if current_role and current_message:
                transcript.append({
                    "role": current_role,
                    "message": ' '.join(current_message)
                })
            current_role = "supplier"
            current_message = [line.split(':', 1)[1].strip()]
        else:
            if current_message:
                current_message.append(line)
            else:
                # Default to buyer if no role specified
                current_role = "buyer"
                current_message = [line]
    
    # Add the last message
    if current_role and current_message:
        transcript.append({
            "role": current_role,
            "message": ' '.join(current_message)
        })
    
    return transcript

async def _analyze_transcript(transcript_data: List[Dict[str, str]]) -> Dict[str, Any]:
    """Perform comprehensive transcript analysis"""
    
    analysis = {
        "summary": {},
        "sentiment_analysis": {},
        "strategy_analysis": {},
        "conversation_flow": {},
        "key_metrics": {},
        "improvement_areas": [],
        "strengths": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # Basic summary
    analysis["summary"] = _generate_basic_summary(transcript_data)
    
    # Sentiment analysis using LLM
    try:
        analysis["sentiment_analysis"] = await llm_service.analyze_conversation_sentiment(transcript_data)
    except Exception as e:
        logger.error(f"LLM sentiment analysis failed: {str(e)}")
        analysis["sentiment_analysis"] = {
            "buyer_sentiment": {"score": 0, "label": "error", "confidence": 0},
            "supplier_sentiment": {"score": 0, "label": "error", "confidence": 0},
            "overall_sentiment": {"score": 0, "label": "error", "confidence": 0},
            "error": f"LLM call didn't work: {str(e)}"
        }
    
    # Strategy analysis
    analysis["strategy_analysis"] = _analyze_strategies(transcript_data)
    
    # Conversation flow
    analysis["conversation_flow"] = _analyze_conversation_flow(transcript_data)
    
    # Key metrics
    analysis["key_metrics"] = _calculate_key_metrics(transcript_data)
    
    # Identify improvement areas and strengths
    analysis["improvement_areas"] = _identify_improvement_areas(transcript_data)
    analysis["strengths"] = _identify_strengths(transcript_data)
    
    return analysis

def _generate_basic_summary(transcript_data: List[Dict[str, str]]) -> Dict[str, Any]:
    """Generate basic summary of the negotiation"""
    buyer_messages = [msg for msg in transcript_data if msg.get("role") == "buyer"]
    supplier_messages = [msg for msg in transcript_data if msg.get("role") == "supplier"]
    
    total_messages = len(transcript_data)
    buyer_word_count = sum(len(msg.get("message", "").split()) for msg in buyer_messages)
    supplier_word_count = sum(len(msg.get("message", "").split()) for msg in supplier_messages)
    
    return {
        "total_messages": total_messages,
        "buyer_messages": len(buyer_messages),
        "supplier_messages": len(supplier_messages),
        "buyer_word_count": buyer_word_count,
        "supplier_word_count": supplier_word_count,
        "average_message_length": (buyer_word_count + supplier_word_count) / total_messages if total_messages > 0 else 0,
        "conversation_balance": len(buyer_messages) / len(supplier_messages) if supplier_messages else 0
    }


def _analyze_strategies(transcript_data: List[Dict[str, str]]) -> Dict[str, Any]:
    """Analyze negotiation strategies used"""
    
    buyer_strategies = _identify_buyer_strategies(transcript_data)
    supplier_strategies = _identify_supplier_strategies(transcript_data)
    
    return {
        "buyer_strategies": buyer_strategies,
        "supplier_strategies": supplier_strategies,
        "strategy_effectiveness": _assess_strategy_effectiveness(buyer_strategies, supplier_strategies)
    }

def _identify_buyer_strategies(transcript_data: List[Dict[str, str]]) -> List[str]:
    """Identify strategies used by the buyer"""
    strategies = []
    buyer_messages = [msg.get("message", "").lower() for msg in transcript_data if msg.get("role") == "buyer"]
    
    all_buyer_text = " ".join(buyer_messages)
    
    # Check for common negotiation strategies
    if any(word in all_buyer_text for word in ['competitor', 'alternative', 'other supplier']):
        strategies.append("competition_leverage")
    
    if any(word in all_buyer_text for word in ['volume', 'bulk', 'large order']):
        strategies.append("volume_leverage")
    
    if any(word in all_buyer_text for word in ['long term', 'partnership', 'relationship']):
        strategies.append("relationship_building")
    
    if any(word in all_buyer_text for word in ['market', 'industry', 'trend']):
        strategies.append("market_pressure")
    
    if any(word in all_buyer_text for word in ['urgent', 'asap', 'immediately']):
        strategies.append("urgency_pressure")
    
    if any(word in all_buyer_text for word in ['budget', 'cost', 'price', 'discount']):
        strategies.append("price_focus")
    
    return strategies

def _identify_supplier_strategies(transcript_data: List[Dict[str, str]]) -> List[str]:
    """Identify strategies used by the supplier"""
    strategies = []
    supplier_messages = [msg.get("message", "").lower() for msg in transcript_data if msg.get("role") == "supplier"]
    
    all_supplier_text = " ".join(supplier_messages)
    
    # Check for common supplier strategies
    if any(word in all_supplier_text for word in ['quality', 'standard', 'value']):
        strategies.append("value_proposition")
    
    if any(word in all_supplier_text for word in ['cost', 'price', 'market']):
        strategies.append("cost_justification")
    
    if any(word in all_supplier_text for word in ['relationship', 'partnership', 'long term']):
        strategies.append("relationship_focus")
    
    if any(word in all_supplier_text for word in ['difficult', 'challenge', 'concern']):
        strategies.append("resistance")
    
    if any(word in all_supplier_text for word in ['alternative', 'option', 'solution']):
        strategies.append("alternative_offering")
    
    return strategies

def _assess_strategy_effectiveness(buyer_strategies: List[str], supplier_strategies: List[str]) -> Dict[str, Any]:
    """Assess the effectiveness of strategies used"""
    return {
        "buyer_strategy_count": len(buyer_strategies),
        "supplier_strategy_count": len(supplier_strategies),
        "strategy_diversity": len(set(buyer_strategies + supplier_strategies)),
        "balanced_negotiation": abs(len(buyer_strategies) - len(supplier_strategies)) <= 2
    }

def _analyze_conversation_flow(transcript_data: List[Dict[str, str]]) -> Dict[str, Any]:
    """Analyze the flow and structure of the conversation"""
    
    # Analyze message patterns
    message_patterns = []
    for i, msg in enumerate(transcript_data):
        role = msg.get("role", "unknown")
        message_length = len(msg.get("message", "").split())
        message_patterns.append({
            "position": i,
            "role": role,
            "length": message_length
        })
    
    # Calculate conversation metrics
    total_length = sum(pattern["length"] for pattern in message_patterns)
    avg_length = total_length / len(message_patterns) if message_patterns else 0
    
    # Identify conversation phases
    phases = _identify_conversation_phases(transcript_data)
    
    return {
        "message_patterns": message_patterns,
        "average_message_length": avg_length,
        "conversation_phases": phases,
        "conversation_length": len(transcript_data)
    }

def _identify_conversation_phases(transcript_data: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Identify different phases of the negotiation"""
    phases = []
    total_messages = len(transcript_data)
    
    if total_messages == 0:
        return phases
    
    # Simple phase identification based on position
    phase_size = max(1, total_messages // 4)  # Divide into roughly 4 phases
    
    phases = [
        {"name": "opening", "messages": transcript_data[:phase_size]},
        {"name": "exploration", "messages": transcript_data[phase_size:phase_size*2]},
        {"name": "negotiation", "messages": transcript_data[phase_size*2:phase_size*3]},
        {"name": "closing", "messages": transcript_data[phase_size*3:]}
    ]
    
    return phases

def _calculate_key_metrics(transcript_data: List[Dict[str, str]]) -> Dict[str, Any]:
    """Calculate key negotiation metrics"""
    
    buyer_messages = [msg for msg in transcript_data if msg.get("role") == "buyer"]
    supplier_messages = [msg for msg in transcript_data if msg.get("role") == "supplier"]
    
    # Calculate response times (simplified)
    response_times = []
    for i in range(1, len(transcript_data)):
        if transcript_data[i]["role"] != transcript_data[i-1]["role"]:
            response_times.append(1)  # Simplified: assume 1 unit time
    
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    return {
        "total_duration": len(transcript_data),
        "average_response_time": avg_response_time,
        "buyer_participation": len(buyer_messages) / len(transcript_data) if transcript_data else 0,
        "supplier_participation": len(supplier_messages) / len(transcript_data) if transcript_data else 0,
        "conversation_turn_count": len(transcript_data)
    }

def _identify_improvement_areas(transcript_data: List[Dict[str, str]]) -> List[str]:
    """Identify areas for improvement"""
    improvements = []
    
    buyer_messages = [msg for msg in transcript_data if msg.get("role") == "buyer"]
    supplier_messages = [msg for msg in transcript_data if msg.get("role") == "supplier"]
    
    # Check for common improvement areas
    if len(buyer_messages) < 2:
        improvements.append("Buyer should engage more actively in the conversation")
    
    if len(supplier_messages) > len(buyer_messages) * 2:
        improvements.append("Buyer should take more initiative in the negotiation")
    
    # Check for price focus
    buyer_text = " ".join([msg.get("message", "").lower() for msg in buyer_messages])
    if 'price' in buyer_text and 'discount' not in buyer_text:
        improvements.append("Consider asking for specific discounts or price reductions")
    
    # Check for leverage usage
    if not any(word in buyer_text for word in ['volume', 'competitor', 'market', 'long term']):
        improvements.append("Consider using leverage points like volume, competition, or long-term relationship")
    
    return improvements

def _identify_strengths(transcript_data: List[Dict[str, str]]) -> List[str]:
    """Identify negotiation strengths"""
    strengths = []
    
    buyer_messages = [msg for msg in transcript_data if msg.get("role") == "buyer"]
    buyer_text = " ".join([msg.get("message", "").lower() for msg in buyer_messages])
    
    # Check for strengths
    if any(word in buyer_text for word in ['please', 'thank', 'appreciate']):
        strengths.append("Maintained professional and polite tone")
    
    if any(word in buyer_text for word in ['volume', 'bulk', 'large order']):
        strengths.append("Used volume as leverage effectively")
    
    if any(word in buyer_text for word in ['long term', 'partnership', 'relationship']):
        strengths.append("Emphasized relationship building")
    
    if len(buyer_messages) >= 3:
        strengths.append("Maintained consistent engagement throughout the negotiation")
    
    return strengths
