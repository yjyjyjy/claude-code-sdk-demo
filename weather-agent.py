#!/usr/bin/env python3
"""
Working Data Analytics Demo - Properly passes execution results between turns
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from logger_util import init_logging, get_logger

load_dotenv()

# legal-agent.py
import asyncio
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

async def main():
    # Configure the weather MCP server
    mcp_servers = {
        "weather": {
            "command": "/Users/junyu/code/claude-code-playground/mcp/weather/.venv/bin/python",
            "args": ["/Users/junyu/code/claude-code-playground/mcp/weather/weather.py"]
        }
    }
    
    # Configure allowed tools (MCP tools follow pattern: mcp__<server>__<tool>)
    allowed_tools = [
        "mcp__weather__get_alerts",
        "mcp__weather__get_forecast"
    ]

    disallowed_tools =  ['Bash', 'Glob', 'Grep', 'LS', 'Read', 'Edit', 'MultiEdit', 'Write', 'NotebookEdit', 'WebFetch', 'WebSearch', 'BashOutput', 'KillBash']
    
    async with ClaudeSDKClient(
        options=ClaudeCodeOptions(
            system_prompt="You are a weather assistant that can check weather forecasts and alerts. Use the available tools to get current weather data from the National Weather Service.",
            max_turns=3,
            model="claude-sonnet-4-0",
            mcp_servers=mcp_servers,
            allowed_tools=allowed_tools,
            disallowed_tools=disallowed_tools
        )
    ) as client:
        # Send the query
        print("🌦️  Requesting comprehensive weather info for San Francisco...")
        await client.query(
            "Please provide complete weather information for San Francisco: 1) Get the weather forecast for coordinates 37.7749, -122.4194 and 2) Check for any weather alerts in California (CA). Use the appropriate weather tools to get this data."
        )
        
        # Stream the response
        print("\n📡 Receiving response...")
        async for message in client.receive_response():
            print(f"🌀 Debug: Message: {message}")
            if hasattr(message, 'content'):
                # Print streaming content as it arrives
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(block.text, end='', flush=True)
            if hasattr(message, 'total_cost_usd'):
                print(f"\n💰 Total cost: ${message.total_cost_usd:.4f}")
        
        print("\n✅ Weather agent completed!")

if __name__ == "__main__":
    asyncio.run(main())