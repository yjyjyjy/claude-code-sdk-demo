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
    async with ClaudeSDKClient(
        options=ClaudeCodeOptions(
            system_prompt="You are a weather assistant. Check the weather forecast for a given location.",
            max_turns=1,
            model="claude-sonnet-4-0"
        )
    ) as client:
        # Send the query
        await client.query(
            "Let me know the weather forecast for San Francisco (37.7749, -122.4194)"
        )
        
        # Stream the response
        async for message in client.receive_response():
            if hasattr(message, 'content'):
                # Print streaming content as it arrives
                for block in message.content:
                    if hasattr(block, 'text'):
                        print(block.text, end='', flush=True)

if __name__ == "__main__":
    asyncio.run(main())