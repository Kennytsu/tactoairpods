"""
Simulate Supplier Response Tool

This module provides functionality to generate realistic supplier responses
during negotiation using LLM integration.
"""

import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime

from .llm_service import llm_service

logger = logging.getLogger(__name__)

async def simulate_supplier_response_tool(
    user_message: str, 
    session_context: Dict[str, Any],
    negotiation_transcript: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Generate a realistic supplier response during negotiation.
    
    Args:
        user_message: The buyer's negotiation message
        session_context: Session context containing supplier data
        negotiation_transcript: Previous conversation history
        
    Returns:
        Dictionary containing the supplier's response and metadata
    """
    try:
        supplier_data = session_context.get('supplier_data', {})
        
        if not supplier_data:
            return {
                "response": "I don't have any supplier data loaded. Please analyze a supplier file first.",
                "confidence": 0.0,
                "strategy": "no_data"
            }
        
        # Generate response based on supplier data and message analysis
        response_data = await _generate_supplier_response(
            user_message, 
            supplier_data, 
            negotiation_transcript
        )
        
        logger.info(f"Generated supplier response for message: {user_message[:50]}...")
        return response_data
        
    except Exception as e:
        logger.error(f"Error generating supplier response: {str(e)}")
        return {
            "response": f"I apologize, but I'm having trouble processing your request right now. {str(e)}",
            "confidence": 0.0,
            "strategy": "error"
        }

async def _generate_supplier_response(
    user_message: str,
    supplier_data: Dict[str, Any],
    transcript: List[Dict[str, str]]
) -> Dict[str, Any]:
    """Generate the actual supplier response"""
    
    # Analyze the user's message to determine negotiation intent
    message_analysis = _analyze_user_message(user_message)
    
    # Determine supplier strategy based on data and history
    strategy = _determine_supplier_strategy(supplier_data, transcript, message_analysis)
    
    # Generate response using LLM
    try:
        response = await llm_service.generate_supplier_response(
            user_message,
            supplier_data,
            transcript,
            strategy
        )
    except Exception as e:
        logger.error(f"LLM generation failed: {str(e)}")
        return {
            "response": f"LLM call didn't work: {str(e)}",
            "confidence": 0.0,
            "strategy": "error",
            "message_analysis": message_analysis
        }
    
    return {
        "response": response,
        "confidence": _calculate_confidence(supplier_data, message_analysis),
        "strategy": strategy,
        "message_analysis": message_analysis
    }

def _analyze_user_message(message: str) -> Dict[str, Any]:
    """Analyze the user's message to understand negotiation intent"""
    message_lower = message.lower()
    
    analysis = {
        "intent": "general",
        "urgency": "normal",
        "price_focus": False,
        "volume_focus": False,
        "quality_focus": False,
        "delivery_focus": False,
        "tone": "professional",
        "leverage_points": []
    }
    
    # Determine intent
    if any(word in message_lower for word in ['discount', 'reduce', 'lower', 'cheaper', 'price']):
        analysis["intent"] = "price_reduction"
        analysis["price_focus"] = True
    
    elif any(word in message_lower for word in ['volume', 'quantity', 'bulk', 'more', 'increase']):
        analysis["intent"] = "volume_increase"
        analysis["volume_focus"] = True
    
    elif any(word in message_lower for word in ['quality', 'standard', 'specification', 'defect']):
        analysis["intent"] = "quality_discussion"
        analysis["quality_focus"] = True
    
    elif any(word in message_lower for word in ['delivery', 'shipping', 'timeline', 'schedule']):
        analysis["intent"] = "delivery_discussion"
        analysis["delivery_focus"] = True
    
    # Determine urgency
    if any(word in message_lower for word in ['urgent', 'asap', 'immediately', 'quickly']):
        analysis["urgency"] = "high"
    elif any(word in message_lower for word in ['soon', 'priority', 'important']):
        analysis["urgency"] = "medium"
    
    # Determine tone
    if any(word in message_lower for word in ['please', 'thank', 'appreciate', 'would like']):
        analysis["tone"] = "polite"
    elif any(word in message_lower for word in ['must', 'require', 'need', 'demand']):
        analysis["tone"] = "demanding"
    elif any(word in message_lower for word in ['unacceptable', 'disappointed', 'concerned']):
        analysis["tone"] = "negative"
    
    # Identify leverage points
    if any(word in message_lower for word in ['competitor', 'alternative', 'other supplier']):
        analysis["leverage_points"].append("competition")
    if any(word in message_lower for word in ['long term', 'partnership', 'relationship']):
        analysis["leverage_points"].append("relationship")
    if any(word in message_lower for word in ['market', 'industry', 'trend']):
        analysis["leverage_points"].append("market_conditions")
    
    return analysis

def _determine_supplier_strategy(
    supplier_data: Dict[str, Any],
    transcript: List[Dict[str, str]],
    message_analysis: Dict[str, Any]
) -> str:
    """Determine the supplier's negotiation strategy"""
    
    # Count previous exchanges
    supplier_messages = [msg for msg in transcript if msg.get("role") == "supplier"]
    buyer_messages = [msg for msg in transcript if msg.get("role") == "buyer"]
    
    # Base strategy on supplier data characteristics
    strategy_factors = []
    
    # Price sensitivity
    if supplier_data.get("prices"):
        avg_price = sum(supplier_data["prices"]) / len(supplier_data["prices"])
        if avg_price > 1000:  # High-value products
            strategy_factors.append("premium")
        else:
            strategy_factors.append("competitive")
    
    # Quality metrics influence
    if supplier_data.get("quality_metrics"):
        avg_quality = sum(supplier_data["quality_metrics"]) / len(supplier_data["quality_metrics"])
        if avg_quality > 8.0:
            strategy_factors.append("quality_focused")
        else:
            strategy_factors.append("cost_focused")
    
    # Delivery performance
    if supplier_data.get("delivery_times"):
        avg_delivery = sum(supplier_data["delivery_times"]) / len(supplier_data["delivery_times"])
        if avg_delivery < 7:
            strategy_factors.append("fast_delivery")
        else:
            strategy_factors.append("standard_delivery")
    
    # Determine strategy based on factors and conversation history
    if len(supplier_messages) == 0:
        return "initial_response"
    elif len(supplier_messages) < 2:
        return "building_relationship"
    elif message_analysis["tone"] == "demanding":
        return "defensive"
    elif "competition" in message_analysis["leverage_points"]:
        return "competitive"
    elif message_analysis["urgency"] == "high":
        return "opportunistic"
    elif message_analysis["price_focus"] and len(supplier_messages) >= 2:
        return "collaborative"  # More willing to negotiate on price
    else:
        return "collaborative"



def _calculate_confidence(supplier_data: Dict[str, Any], message_analysis: Dict[str, Any]) -> float:
    """Calculate confidence score for the response"""
    confidence = 0.5  # Base confidence
    
    # Increase confidence based on available data
    if supplier_data.get("supplier_name"):
        confidence += 0.1
    if supplier_data.get("prices"):
        confidence += 0.1
    if supplier_data.get("products"):
        confidence += 0.1
    if supplier_data.get("quality_metrics"):
        confidence += 0.1
    if supplier_data.get("delivery_times"):
        confidence += 0.1
    
    # Adjust based on message clarity
    if message_analysis["intent"] != "general":
        confidence += 0.1
    
    return min(confidence, 1.0)
