#!/usr/bin/env python3
"""
MCP Host for TactoLearn Negotiation Intelligence Agent

This module provides the MCP host that manages negotiation training tools
and maintains session context for supplier data.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
)

# Import our custom tools
from tools.analyze_supplier import analyze_supplier_tool
from tools.simulate_supplier_response import simulate_supplier_response_tool
from tools.summarize_negotiation_transcript import summarize_negotiation_transcript_tool
from tools.generate_feedback import generate_feedback_tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NegotiationTrainerHost:
    """MCP Host for the Negotiation Trainer Agent"""
    
    def __init__(self):
        self.server = Server("negotiation-trainer")
        self.session_context: Dict[str, Any] = {}
        self.negotiation_transcript: List[Dict[str, str]] = []
        
        # Register tools
        self._register_tools()
        
    def _register_tools(self):
        """Register all negotiation training tools"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available negotiation training tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="analyze_supplier",
                        description="Analyze supplier data from CSV or PDF files to extract pricing, delivery times, quality metrics, and past purchase volumes",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "Path to the supplier data file (CSV or PDF)"
                                }
                            },
                            "required": ["file_path"]
                        }
                    ),
                    Tool(
                        name="simulate_supplier_response",
                        description="Generate a realistic supplier response during negotiation based on analyzed supplier data",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_message": {
                                    "type": "string",
                                    "description": "The buyer's negotiation message"
                                }
                            },
                            "required": ["user_message"]
                        }
                    ),
                    Tool(
                        name="summarize_negotiation_transcript",
                        description="Analyze a negotiation transcript to extract key metrics, sentiment, and strategy patterns",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "transcript_path": {
                                    "type": "string",
                                    "description": "Path to the negotiation transcript file"
                                }
                            },
                            "required": ["transcript_path"]
                        }
                    ),
                    Tool(
                        name="generate_feedback",
                        description="Generate training feedback and improvement suggestions based on negotiation analysis",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "report_data": {
                                    "type": "object",
                                    "description": "The negotiation analysis report data"
                                }
                            },
                            "required": ["report_data"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "analyze_supplier":
                    result = await analyze_supplier_tool(arguments["file_path"], self.session_context)
                    return CallToolResult(
                        content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                    )
                
                elif name == "simulate_supplier_response":
                    result = await simulate_supplier_response_tool(
                        arguments["user_message"], 
                        self.session_context,
                        self.negotiation_transcript
                    )
                    # Add to transcript
                    self.negotiation_transcript.append({
                        "role": "buyer",
                        "message": arguments["user_message"]
                    })
                    self.negotiation_transcript.append({
                        "role": "supplier",
                        "message": result["response"]
                    })
                    return CallToolResult(
                        content=[TextContent(type="text", text=result["response"])]
                    )
                
                elif name == "summarize_negotiation_transcript":
                    result = await summarize_negotiation_transcript_tool(
                        arguments["transcript_path"],
                        self.negotiation_transcript
                    )
                    return CallToolResult(
                        content=[TextContent(type="text", text=json.dumps(result, indent=2))]
                    )
                
                elif name == "generate_feedback":
                    result = await generate_feedback_tool(arguments["report_data"])
                    return CallToolResult(
                        content=[TextContent(type="text", text=result)]
                    )
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error calling tool {name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="negotiation-trainer",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

async def main():
    """Main entry point"""
    host = NegotiationTrainerHost()
    await host.run()

if __name__ == "__main__":
    asyncio.run(main())



