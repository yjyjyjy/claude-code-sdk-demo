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
            system_prompt="You are a legal assistant. Identify risks and suggest improvements.",
            max_turns=2,
            model="claude-sonnet-4-0"
        )
    ) as client:
        # Send the query
        await client.query(
            "Review this contract clause for potential issues: 'The party agrees to unlimited liability...'"
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