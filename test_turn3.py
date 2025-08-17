#!/usr/bin/env python3
"""
Test Turn 3 - Chart Analysis with existing analytics_chart.png
"""

import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
from logger_util import init_logging, get_logger

load_dotenv()

try:
    from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
except ImportError as e:
    print(f"Import error: {e}")
    exit(1)


async def test_turn3_only():
    """Test only Turn 3 - Chart analysis with existing chart"""
    
    # Initialize logging
    logger = init_logging()
    
    print("\n🔍 Testing Turn 3: Chart Analysis Only")
    print("=" * 50)
    print(f"📝 Logging to: {logger.log_file}")
    
    # Check if chart exists
    chart_path = Path('analytics_chart.png')
    if not chart_path.exists():
        print("❌ analytics_chart.png not found! Please generate it first.")
        return {'success': False, 'error': 'Chart file not found'}
    
    print(f"✅ Found chart: {chart_path}")
    
    options = ClaudeCodeOptions(
        system_prompt="You are a data analyst. Analyze the provided chart image.",
        max_turns=5
    )
    
    async with ClaudeSDKClient(options=options) as client:
        
        # Sample revenue data (from previous runs)
        revenue_dict = {'Accessories': 10675, 'Electronics': 68400}
        
        # Use absolute path for the chart
        chart_abs_path = chart_path.absolute()
        
        query3 = f"""I created a chart showing revenue by category with these values:
{revenue_dict}

Please analyze this chart image {chart_abs_path} and provide:
1. Key insights from the visualization
2. Which category performs better
3. Business recommendations based on the data shown"""
        
        print("\n🔍 TURN 3: Chart Analysis")
        print("-" * 40)
        print("Sending chart analysis request...")
        
        # Log query with attachment
        logger.log_query(query3, turn=3, attachments=[str(chart_path)])
        
        # Send query - Claude will automatically read the image file mentioned in prompt
        await client.query(query3)
        
        response3 = ""
        cost3 = 0
        session_id = None
        
        async for message in client.receive_response():
            # Log the complete response object
            logger.log_response(message, turn=3)
            
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        text = block.text
                        response3 += text
                        print(text, end='', flush=True)
            
            if type(message).__name__ == "ResultMessage":
                cost3 = getattr(message, 'total_cost_usd', 0)
                session_id = getattr(message, 'session_id', None)
                print(f"\n💰 Turn 3 Cost: ${cost3:.4f}")
        
        print(f"\n\n🎯 TURN 3 TEST COMPLETE")
        print("=" * 40)
        print(f"💰 Cost: ${cost3:.4f}")
        print(f"🆔 Session: {session_id}")
        print(f"📊 Chart analyzed: Yes")
        print(f"📄 Response length: {len(response3)} characters")
        
        final_result = {
            'success': True,
            'cost': cost3,
            'session_id': session_id,
            'response_length': len(response3),
            'chart_path': str(chart_path)
        }
        
        # Close logging session
        logger.close_session(final_result)
        print(f"📝 Complete session log saved to: {logger.log_file}")
        
        return final_result


async def main():
    try:
        result = await test_turn3_only()
        print(f"\n✅ Turn 3 test result: {result}")
        
    except Exception as e:
        print(f"\n❌ Turn 3 test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())