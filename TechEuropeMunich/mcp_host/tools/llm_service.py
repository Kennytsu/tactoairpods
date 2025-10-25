"""
LLM Service for TactoLearn Negotiation Intelligence Agent

This module provides LLM integration for generating realistic supplier responses
and analyzing negotiation conversations.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import openai
from anthropic import Anthropic

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with various LLM providers"""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.timeout = int(os.getenv("API_TIMEOUT", "30"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1000"))
        
        # Initialize clients based on provider
        if self.provider == "openai":
            self.openai_client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        elif self.provider == "anthropic":
            self.anthropic_client = Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def generate_supplier_response(
        self,
        user_message: str,
        supplier_data: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        strategy: str
    ) -> str:
        """Generate a realistic supplier response using LLM"""
        
        try:
            # Build context for the LLM
            context = self._build_supplier_context(supplier_data, conversation_history, strategy)
            
            # Create the prompt
            prompt = self._create_supplier_prompt(user_message, context, strategy)
            
            # Generate response
            response = await self._call_llm(prompt)
            
            logger.info(f"Generated LLM response using {self.provider}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            # Return error message instead of fallback
            return f"LLM call didn't work: {str(e)}"
    
    async def analyze_conversation_sentiment(
        self,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Analyze conversation sentiment using LLM"""
        
        try:
            conversation_text = self._format_conversation_for_analysis(messages)
            
            prompt = f"""
            Analyze the sentiment and tone of this negotiation conversation between a buyer and supplier.
            
            Conversation:
            {conversation_text}
            
            Please provide a JSON response with:
            - buyer_sentiment: "positive", "negative", or "neutral"
            - supplier_sentiment: "positive", "negative", or "neutral"
            - overall_tone: "professional", "aggressive", "collaborative", or "defensive"
            - key_emotions: array of emotions detected
            - confidence: confidence score (0-1)
            
            Respond only with valid JSON.
            """
            
            response = await self._call_llm(prompt)
            
            # Try to parse JSON response
            import json
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Return error instead of fallback
                return {
                    "buyer_sentiment": {"score": 0, "label": "error", "confidence": 0},
                    "supplier_sentiment": {"score": 0, "label": "error", "confidence": 0},
                    "overall_tone": "error",
                    "key_emotions": [],
                    "confidence": 0,
                    "error": "Failed to parse LLM response"
                }
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment with LLM: {str(e)}")
            return {
                "buyer_sentiment": {"score": 0, "label": "error", "confidence": 0},
                "supplier_sentiment": {"score": 0, "label": "error", "confidence": 0},
                "overall_tone": "error",
                "key_emotions": [],
                "confidence": 0,
                "error": f"LLM call didn't work: {str(e)}"
            }
    
    async def generate_training_feedback(
        self,
        analysis_data: Dict[str, Any],
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Generate detailed training feedback using LLM"""
        
        try:
            conversation_text = self._format_conversation_for_analysis(conversation_history)
            
            prompt = f"""
            You are an expert negotiation coach. Analyze this negotiation conversation and provide detailed feedback.
            
            Conversation:
            {conversation_text}
            
            Analysis Data:
            {analysis_data}
            
            Please provide comprehensive feedback including:
            1. Executive Summary of the negotiation
            2. Strengths demonstrated by the buyer
            3. Areas for improvement
            4. Specific recommendations for next time
            5. Strategic insights about the supplier's behavior
            
            Format your response as a professional training report with clear sections and actionable advice.
            """
            
            response = await self._call_llm(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error generating feedback with LLM: {str(e)}")
            return "Error generating feedback. Please try again."
    
    def _build_supplier_context(
        self,
        supplier_data: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        strategy: str
    ) -> str:
        """Build context string for supplier response generation"""
        
        context_parts = []
        
        # Supplier information
        if supplier_data.get("supplier_name"):
            context_parts.append(f"Supplier: {supplier_data['supplier_name']}")
        
        if supplier_data.get("products"):
            products = supplier_data["products"][:5]  # Limit to 5 products
            context_parts.append(f"Products: {', '.join(products)}")
        
        if supplier_data.get("prices"):
            prices = supplier_data["prices"][:5]  # Limit to 5 prices
            avg_price = sum(prices) / len(prices)
            context_parts.append(f"Average price: ${avg_price:.2f}")
        
        if supplier_data.get("quality_metrics"):
            quality_scores = supplier_data["quality_metrics"][:5]
            avg_quality = sum(quality_scores) / len(quality_scores)
            context_parts.append(f"Quality rating: {avg_quality:.1f}/10")
        
        if supplier_data.get("delivery_times"):
            delivery_times = supplier_data["delivery_times"][:5]
            avg_delivery = sum(delivery_times) / len(delivery_times)
            context_parts.append(f"Average delivery time: {avg_delivery:.0f} days")
        
        # Conversation context
        if conversation_history:
            recent_messages = conversation_history[-4:]  # Last 4 messages
            context_parts.append("Recent conversation:")
            for msg in recent_messages:
                role = msg.get("role", "unknown")
                message = msg.get("message", "")[:100]  # Truncate long messages
                context_parts.append(f"  {role}: {message}")
        
        return "\n".join(context_parts)
    
    def _create_supplier_prompt(
        self,
        user_message: str,
        context: str,
        strategy: str
    ) -> str:
        """Create prompt for supplier response generation"""
        
        strategy_instructions = {
            "initial_response": "Respond naturally and show genuine interest in the buyer's needs.",
            "building_relationship": "Be warm and collaborative, focus on understanding their requirements.",
            "defensive": "Be cautious but not overly formal. Show some resistance while staying professional.",
            "competitive": "Emphasize your strengths confidently but don't be arrogant.",
            "opportunistic": "Recognize their urgency and be more direct about what you can offer.",
            "collaborative": "Work together to find solutions. Be flexible and show willingness to negotiate."
        }
        
        instruction = strategy_instructions.get(strategy, "Respond naturally and professionally to the buyer's message.")
        
        prompt = f"""
        You are a real supplier representative in a business negotiation. Be human, not robotic.
        
        Context about your company:
        {context}
        
        Current negotiation strategy: {strategy}
        Instruction: {instruction}
        
        Buyer's message: "{user_message}"
        
        Respond as a REAL supplier would:
        - Be conversational and natural, not overly formal
        - Don't say "thank you" in every response
        - Show genuine interest in their business
        - Be willing to negotiate and make concessions when appropriate
        - Use realistic business language, not corporate speak
        - Show personality and human traits
        - Be direct about pricing, discounts, and terms when asked
        - Don't always deflect - sometimes give specific answers
        
        Examples of good responses:
        - "For 1000 units, I can offer you 8% off our standard pricing"
        - "Our delivery time is typically 2 weeks, but we can rush it to 5 days for an extra 15%"
        - "I understand budget constraints. Let me see what we can work out"
        - "That's a significant order. I'll need to check with my manager on pricing"
        
        Keep your response conversational and realistic (2-3 sentences max).
        """
        
        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the appropriate LLM provider"""
        
        if self.provider == "openai":
            return await self._call_openai(prompt)
        elif self.provider == "anthropic":
            return await self._call_anthropic(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specializing in business negotiations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API"""
        try:
            response = self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    def _format_conversation_for_analysis(self, messages: List[Dict[str, str]]) -> str:
        """Format conversation for LLM analysis"""
        formatted = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("message", "")
            formatted.append(f"{role.title()}: {content}")
        return "\n".join(formatted)
    

# Global LLM service instance
llm_service = LLMService()
