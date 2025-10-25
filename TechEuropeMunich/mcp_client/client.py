#!/usr/bin/env python3
"""
MCP Client for TactoLearn Negotiation Intelligence Agent

This module provides a simple client interface for connecting to the MCP host
and testing the negotiation training tools.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NegotiationTrainerClient:
    """Client for the Negotiation Trainer MCP Agent"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.available_tools: List[Dict[str, Any]] = []
        
    async def connect(self, host_command: List[str]):
        """Connect to the MCP host"""
        try:
            server_params = StdioServerParameters(
                command=host_command[0],
                args=host_command[1:] if len(host_command) > 1 else []
            )
            
            # Use the context manager properly
            async with stdio_client(server_params) as (read_stream, write_stream):
                self.session = ClientSession(read_stream, write_stream)
                
                # Initialize the session
                await self.session.initialize()
                
                # List available tools
                tools_result = await self.session.list_tools()
                self.available_tools = tools_result.tools
                
                logger.info(f"Connected to MCP host. Available tools: {len(self.available_tools)}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP host: {str(e)}")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP host"""
        if not self.session:
            raise RuntimeError("Not connected to MCP host")
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            
            # Extract text content from result
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return {"success": True, "result": content.text}
                else:
                    return {"success": True, "result": str(content)}
            else:
                return {"success": True, "result": "No content returned"}
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def analyze_supplier(self, file_path: str) -> Dict[str, Any]:
        """Analyze supplier data from a file"""
        return await self.call_tool("analyze_supplier", {"file_path": file_path})
    
    async def simulate_supplier_response(self, user_message: str) -> Dict[str, Any]:
        """Simulate a supplier response to user message"""
        return await self.call_tool("simulate_supplier_response", {"user_message": user_message})
    
    async def summarize_transcript(self, transcript_path: str = None) -> Dict[str, Any]:
        """Summarize negotiation transcript"""
        args = {}
        if transcript_path:
            args["transcript_path"] = transcript_path
        return await self.call_tool("summarize_negotiation_transcript", args)
    
    async def generate_feedback(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate feedback from analysis report"""
        return await self.call_tool("generate_feedback", {"report_data": report_data})
    
    def list_tools(self):
        """List available tools"""
        print("\nAvailable Tools:")
        print("=" * 50)
        for tool in self.available_tools:
            print(f"• {tool.name}")
            print(f"  Description: {tool.description}")
            print()

async def interactive_mode(client: NegotiationTrainerClient):
    """Run interactive negotiation training session"""
    
    print("\n🎯 TactoLearn Negotiation Intelligence Agent")
    print("=" * 50)
    print("Welcome to your negotiation training session!")
    print("Type 'help' for available commands, 'quit' to exit.")
    print()
    
    while True:
        try:
            command = input("Negotiation Trainer> ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! Keep practicing your negotiation skills!")
                break
            
            elif command.lower() == 'help':
                print_help()
            
            elif command.lower() == 'tools':
                client.list_tools()
            
            elif command.startswith('analyze '):
                file_path = command[8:].strip()
                if file_path:
                    print(f"Analyzing supplier data from: {file_path}")
                    result = await client.analyze_supplier(file_path)
                    if result["success"]:
                        print("✅ Analysis completed successfully!")
                        print(result["result"])
                    else:
                        print(f"❌ Error: {result['error']}")
                else:
                    print("Please provide a file path: analyze <file_path>")
            
            elif command.startswith('negotiate '):
                message = command[10:].strip()
                if message:
                    print(f"You: {message}")
                    result = await client.simulate_supplier_response(message)
                    if result["success"]:
                        print(f"Supplier: {result['result']}")
                    else:
                        print(f"❌ Error: {result['error']}")
                else:
                    print("Please provide a message: negotiate <your_message>")
            
            elif command.lower() == 'summarize':
                print("Analyzing negotiation transcript...")
                result = await client.summarize_transcript()
                if result["success"]:
                    print("✅ Transcript analysis completed!")
                    print(result["result"])
                else:
                    print(f"❌ Error: {result['error']}")
            
            elif command.lower() == 'feedback':
                print("Generating training feedback...")
                # First get the analysis
                analysis_result = await client.summarize_transcript()
                if analysis_result["success"]:
                    try:
                        report_data = json.loads(analysis_result["result"])
                        feedback_result = await client.generate_feedback(report_data)
                        if feedback_result["success"]:
                            print("✅ Feedback generated!")
                            print(feedback_result["result"])
                        else:
                            print(f"❌ Error generating feedback: {feedback_result['error']}")
                    except json.JSONDecodeError:
                        print("❌ Error: Could not parse analysis results")
                else:
                    print(f"❌ Error: Could not analyze transcript: {analysis_result['error']}")
            
            elif command.lower() == 'demo':
                await run_demo(client)
            
            else:
                print("Unknown command. Type 'help' for available commands.")
            
            print()  # Add spacing between commands
            
        except KeyboardInterrupt:
            print("\nGoodbye! Keep practicing your negotiation skills!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")

def print_help():
    """Print help information"""
    print("""
Available Commands:
==================

analyze <file_path>     - Analyze supplier data from CSV or PDF file
negotiate <message>     - Send a negotiation message to the supplier
summarize              - Analyze the current negotiation transcript
feedback               - Generate training feedback and recommendations
tools                  - List all available tools
demo                   - Run a demonstration negotiation
help                   - Show this help message
quit/exit/q            - Exit the application

Example Usage:
=============
1. analyze supplier_data.csv
2. negotiate "We'd like to discuss pricing for our next quarter order"
3. negotiate "What kind of volume discount can you offer?"
4. summarize
5. feedback
""")

async def run_demo(client: NegotiationTrainerClient):
    """Run a demonstration negotiation"""
    print("\n🎬 Running Demo Negotiation")
    print("=" * 30)
    
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
        print(f"[Message {i}] You: {message}")
        
        result = await client.simulate_supplier_response(message)
        if result["success"]:
            print(f"[Response {i}] Supplier: {result['result']}")
        else:
            print(f"❌ Error: {result['error']}")
        
        print()
        
        # Small delay for realism
        await asyncio.sleep(1)
    
    print("Demo negotiation completed!")
    print("Now analyzing the transcript...")
    
    # Analyze the demo
    analysis_result = await client.summarize_transcript()
    if analysis_result["success"]:
        print("✅ Analysis completed!")
        print(analysis_result["result"])
        
        # Generate feedback
        print("\nGenerating feedback...")
        try:
            report_data = json.loads(analysis_result["result"])
            feedback_result = await client.generate_feedback(report_data)
            if feedback_result["success"]:
                print("✅ Feedback generated!")
                print(feedback_result["result"])
            else:
                print(f"❌ Error generating feedback: {feedback_result['error']}")
        except json.JSONDecodeError:
            print("❌ Error: Could not parse analysis results")
    else:
        print(f"❌ Error analyzing transcript: {analysis_result['error']}")

async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_host.py>")
        print("Example: python client.py ../mcp_host/host.py")
        sys.exit(1)
    
    host_path = sys.argv[1]
    if not Path(host_path).exists():
        print(f"Error: Host file not found: {host_path}")
        sys.exit(1)
    
    # Create client and connect
    client = NegotiationTrainerClient()
    
    # Determine Python executable
    python_executable = sys.executable
    
    # Connect to host
    print(f"Connecting to MCP host: {python_executable} {host_path}")
    success = await client.connect([python_executable, host_path])
    
    if not success:
        print("Failed to connect to MCP host. Exiting.")
        sys.exit(1)
    
    print("✅ Connected to MCP host successfully!")
    
    # Run interactive mode
    await interactive_mode(client)

if __name__ == "__main__":
    asyncio.run(main())
