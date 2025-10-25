"""
Generate Feedback Tool

This module provides functionality to generate training feedback and improvement
suggestions based on negotiation analysis results using LLM integration.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .llm_service import llm_service

logger = logging.getLogger(__name__)

async def generate_feedback_tool(report_data: Dict[str, Any]) -> str:
    """
    Generate training feedback and improvement suggestions based on negotiation analysis.
    
    Args:
        report_data: The negotiation analysis report data
        
    Returns:
        Formatted feedback report as a string
    """
    try:
        if not report_data:
            return "No analysis data provided. Please analyze a negotiation transcript first."
        
        # Extract conversation history from report data if available
        conversation_history = report_data.get("conversation_history", [])
        
        # Generate comprehensive feedback using LLM
        try:
            feedback = await llm_service.generate_training_feedback(
                report_data,
                conversation_history
            )
            logger.info("Successfully generated LLM-powered feedback")
            return feedback
        except Exception as e:
            logger.error(f"LLM feedback generation failed: {str(e)}")
            return f"LLM call didn't work: {str(e)}"
        
    except Exception as e:
        logger.error(f"Error generating feedback: {str(e)}")
        return f"Error generating feedback: {str(e)}"

def _generate_executive_summary(report_data: Dict[str, Any]) -> str:
    """Generate executive summary of the negotiation"""
    
    summary_data = report_data.get("summary", {})
    sentiment_data = report_data.get("sentiment_analysis", {})
    strategy_data = report_data.get("strategy_analysis", {})
    
    total_messages = summary_data.get("total_messages", 0)
    buyer_messages = summary_data.get("buyer_messages", 0)
    overall_sentiment = sentiment_data.get("overall_sentiment", {}).get("label", "neutral")
    
    buyer_strategies = strategy_data.get("buyer_strategies", [])
    strategy_count = len(buyer_strategies)
    
    summary = f"""# Negotiation Training Feedback Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

**Negotiation Overview:**
- Total messages exchanged: {total_messages}
- Your participation: {buyer_messages} messages
- Overall sentiment: {overall_sentiment.title()}
- Strategies employed: {strategy_count}

**Key Takeaway:** """
    
    if strategy_count == 0:
        summary += "This negotiation lacked strategic focus. Consider developing a clear negotiation strategy before engaging with suppliers."
    elif strategy_count >= 3:
        summary += "You demonstrated good strategic thinking by employing multiple negotiation approaches."
    else:
        summary += "You used some strategic elements, but there's room to expand your negotiation toolkit."
    
    return summary

def _generate_performance_analysis(report_data: Dict[str, Any]) -> str:
    """Generate performance analysis section"""
    
    summary_data = report_data.get("summary", {})
    sentiment_data = report_data.get("sentiment_analysis", {})
    key_metrics = report_data.get("key_metrics", {})
    
    buyer_sentiment = sentiment_data.get("buyer_sentiment", {})
    supplier_sentiment = sentiment_data.get("supplier_sentiment", {})
    
    conversation_balance = summary_data.get("conversation_balance", 0)
    avg_message_length = summary_data.get("average_message_length", 0)
    
    performance = f"""## Performance Analysis

**Communication Effectiveness:**
- Your sentiment: {buyer_sentiment.get('label', 'neutral').title()} (confidence: {buyer_sentiment.get('confidence', 0):.1%})
- Supplier sentiment: {supplier_sentiment.get('label', 'neutral').title()} (confidence: {supplier_sentiment.get('confidence', 0):.1%})
- Conversation balance: {conversation_balance:.1f} (your messages per supplier message)
- Average message length: {avg_message_length:.1f} words

**Assessment:** """
    
    if conversation_balance < 0.5:
        performance += "You were relatively passive in this negotiation. Consider taking more initiative and asking more questions."
    elif conversation_balance > 2.0:
        performance += "You dominated the conversation. While engagement is good, ensure you're listening to the supplier's responses."
    else:
        performance += "You maintained good conversation balance, allowing for productive dialogue."
    
    if avg_message_length < 10:
        performance += " Your messages were quite brief. Consider providing more context and detail in your requests."
    elif avg_message_length > 50:
        performance += " Your messages were quite lengthy. Consider being more concise to maintain clarity."
    else:
        performance += " Your message length was appropriate for effective communication."
    
    return performance

def _generate_strategy_assessment(report_data: Dict[str, Any]) -> str:
    """Generate strategy assessment section"""
    
    strategy_data = report_data.get("strategy_analysis", {})
    buyer_strategies = strategy_data.get("buyer_strategies", [])
    supplier_strategies = strategy_data.get("supplier_strategies", [])
    effectiveness = strategy_data.get("strategy_effectiveness", {})
    
    strategy_assessment = f"""## Strategy Assessment

**Your Strategies Used:**
{_format_strategies(buyer_strategies)}

**Supplier Strategies Observed:**
{_format_strategies(supplier_strategies)}

**Strategy Effectiveness:**
- Strategy diversity: {effectiveness.get('strategy_diversity', 0)} different approaches
- Balanced negotiation: {'Yes' if effectiveness.get('balanced_negotiation', False) else 'No'}

**Analysis:** """
    
    if not buyer_strategies:
        strategy_assessment += "You didn't employ any clear negotiation strategies. This is a major opportunity for improvement."
    elif len(buyer_strategies) == 1:
        strategy_assessment += "You used a single strategy approach. Consider diversifying your negotiation tactics."
    elif len(buyer_strategies) >= 3:
        strategy_assessment += "You demonstrated good strategic variety. This shows strong negotiation planning."
    else:
        strategy_assessment += "You used some strategic elements effectively. Consider expanding your approach."
    
    return strategy_assessment

def _format_strategies(strategies: List[str]) -> str:
    """Format strategy list for display"""
    if not strategies:
        return "- None identified"
    
    strategy_descriptions = {
        "competition_leverage": "Competition leverage (mentioning alternatives)",
        "volume_leverage": "Volume leverage (bulk ordering)",
        "relationship_building": "Relationship building (long-term partnership)",
        "market_pressure": "Market pressure (industry trends)",
        "urgency_pressure": "Urgency pressure (time constraints)",
        "price_focus": "Price focus (cost discussions)",
        "value_proposition": "Value proposition (quality/service)",
        "cost_justification": "Cost justification (pricing rationale)",
        "relationship_focus": "Relationship focus (partnership emphasis)",
        "resistance": "Resistance (pushback tactics)",
        "alternative_offering": "Alternative offering (solution options)"
    }
    
    formatted = []
    for strategy in strategies:
        description = strategy_descriptions.get(strategy, strategy.replace('_', ' ').title())
        formatted.append(f"- {description}")
    
    return "\n".join(formatted)

def _generate_recommendations(report_data: Dict[str, Any]) -> str:
    """Generate specific recommendations section"""
    
    improvements = report_data.get("improvement_areas", [])
    strengths = report_data.get("strengths", [])
    sentiment_data = report_data.get("sentiment_analysis", {})
    
    recommendations = f"""## Recommendations

**Immediate Improvements:**
{_format_improvements(improvements)}

**Strengths to Build On:**
{_format_strengths(strengths)}

**Strategic Recommendations:** """
    
    # Generate strategic recommendations based on analysis
    buyer_sentiment = sentiment_data.get("buyer_sentiment", {})
    supplier_sentiment = sentiment_data.get("supplier_sentiment", {})
    
    if buyer_sentiment.get("label") == "negative":
        recommendations += "\n- Work on maintaining a more positive tone, even when discussing difficult topics"
    
    if supplier_sentiment.get("label") == "negative":
        recommendations += "\n- Consider how your approach might be affecting the supplier's receptiveness"
    
    if not improvements:
        recommendations += "\n- Continue your current approach while looking for opportunities to add more strategic elements"
    
    return recommendations

def _format_improvements(improvements: List[str]) -> str:
    """Format improvement areas for display"""
    if not improvements:
        return "- No specific improvement areas identified"
    
    formatted = []
    for improvement in improvements:
        formatted.append(f"- {improvement}")
    
    return "\n".join(formatted)

def _format_strengths(strengths: List[str]) -> str:
    """Format strengths for display"""
    if not strengths:
        return "- No specific strengths identified"
    
    formatted = []
    for strength in strengths:
        formatted.append(f"- {strength}")
    
    return "\n".join(formatted)

def _generate_action_items(report_data: Dict[str, Any]) -> str:
    """Generate actionable next steps"""
    
    improvements = report_data.get("improvement_areas", [])
    strategy_data = report_data.get("strategy_analysis", {})
    buyer_strategies = strategy_data.get("buyer_strategies", [])
    
    action_items = f"""## Action Items

**For Your Next Negotiation:**

1. **Preparation Phase:**
   - Research supplier data thoroughly before the negotiation
   - Identify 3-5 key leverage points to use strategically
   - Prepare specific questions about pricing, delivery, and terms

2. **Strategy Development:**
   - Plan your opening approach based on supplier characteristics
   - Prepare fallback positions for key negotiation points
   - Identify win-win opportunities to explore

3. **Communication Skills:**
   - Practice active listening techniques
   - Prepare clear, concise messages for each negotiation point
   - Develop responses for common supplier objections

4. **Specific Focus Areas:** """
    
    # Add specific action items based on analysis
    if not buyer_strategies:
        action_items += "\n   - Learn and practice basic negotiation strategies (volume leverage, competition leverage)"
    
    if "price_focus" not in buyer_strategies:
        action_items += "\n   - Practice price negotiation techniques and discount requests"
    
    if not any(s in buyer_strategies for s in ["volume_leverage", "competition_leverage"]):
        action_items += "\n   - Develop leverage-based negotiation approaches"
    
    action_items += f"""

**Practice Recommendations:**
- Run 2-3 more negotiation simulations with different supplier profiles
- Focus on one improvement area per practice session
- Record your negotiations to track progress over time

**Resources:**
- Review supplier data analysis to understand negotiation context
- Study successful negotiation patterns from previous sessions
- Consider role-playing with colleagues to practice different scenarios"""

    return action_items

