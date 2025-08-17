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

try:
    from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


async def working_demo():
    """Demonstrate proper result passing between turns"""
    
    # Initialize logging
    logger = init_logging()
    
    print("\n🚀 Working Multi-Turn Data Analytics Demo")
    print("="*60)
    print(f"📝 Logging to: {logger.log_file}")
    
    # First, let's examine our data to understand the structure
    df = pd.read_csv('sample_data.csv')
    print(f"📊 Data structure: {df.shape}")
    print(f"📋 Columns: {list(df.columns)}")
    print(f"🔍 First 2 rows:\n{df.head(2)}")
    
    options = ClaudeCodeOptions(
        system_prompt="""You are a data analyst. Format Python code in ```python blocks. 
Use the EXACT column names provided in the data description.""",
        max_turns=4
    )
    
    async with ClaudeSDKClient(options=options) as client:
        
        # TURN 1: Data Analysis
        print(f"\n📊 TURN 1: Data Analysis")
        print("-" * 40)
        
        query1 = f"""I have a CSV file 'sample_data.csv' with these columns:
{list(df.columns)}

First few rows:
{df.head(2).to_string()}

Please generate Python code to:
1. Load the CSV with pandas
2. Show dataset shape and columns
3. Display first 3 rows
4. Calculate total revenue by the 'category' column (NOT product_category!)
5. Store results in a 'result' dictionary

Use EXACT column names shown above."""
        
        print("Sending detailed data analysis request...")
        logger.log_query(query1, turn=1)
        await client.query(query1)
        
        response1 = ""
        cost1 = 0
        session_id = None
        
        async for message in client.receive_response():
            # Log the complete response object
            logger.log_response(message, turn=1)
            
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        text = block.text
                        response1 += text
                        print(text, end='', flush=True)
            
            if type(message).__name__ == "ResultMessage":
                cost1 = getattr(message, 'total_cost_usd', 0)
                session_id = getattr(message, 'session_id', None)
                print(f"\n💰 Turn 1 Cost: ${cost1:.4f}")
        
        # Execute Turn 1 code
        print(f"\n🔧 Executing generated code...")
        
        import re
        code_blocks = re.findall(r'```python\n(.*?)\n```', response1, re.DOTALL)
        
        result1 = None
        if code_blocks:
            code = code_blocks[0].strip()
            print(f"📝 Executing code...")
            
            try:
                exec_globals = {'pd': pd, 'np': np}
                exec(code, exec_globals)
                result1 = exec_globals.get('result')
                logger.log_execution(code, result1, turn=1, success=True)
                print(f"✅ Execution successful!")
                print(f"📊 Result keys: {list(result1.keys()) if result1 else 'None'}")
                
            except Exception as e:
                logger.log_execution(code, None, turn=1, success=False, error=str(e))
                print(f"❌ Error: {e}")
                result1 = None
        
        # TURN 2: Visualization with ACTUAL results
        print(f"\n\n📈 TURN 2: Visualization with Results")
        print("-" * 40)
        
        if result1 and 'revenue_by_category' in result1:
            # Convert pandas Series to dict for JSON serialization
            revenue_data = result1['revenue_by_category']
            if hasattr(revenue_data, 'to_dict'):
                revenue_dict = revenue_data.to_dict()
            else:
                revenue_dict = dict(revenue_data)
            
            query2 = f"""Here are the ACTUAL analysis results from the previous step:

Dataset shape: {result1.get('shape')}
Columns: {result1.get('columns')}
Revenue by category: {revenue_dict}

Now generate Python code to:
1. Load sample_data.csv 
2. Group by 'category' column and sum 'revenue' column
3. Create a bar chart showing these exact values: {revenue_dict}
4. Save as 'analytics_chart.png'
5. Make it well-labeled and professional

Use the EXACT data shown above."""
            
        else:
            query2 = f"""Generate Python code to:
1. Load sample_data.csv (columns: {list(df.columns)})
2. Group by 'category' and sum 'revenue' 
3. Create bar chart and save as 'analytics_chart.png'"""
        
        print("Sending visualization request with actual data...")
        logger.log_query(query2, turn=2)
        await client.query(query2)
        
        response2 = ""
        cost2 = 0
        
        async for message in client.receive_response():
            # Log the complete response object
            logger.log_response(message, turn=2)
            
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        text = block.text
                        response2 += text
                        print(text, end='', flush=True)
            
            if type(message).__name__ == "ResultMessage":
                cost2 = getattr(message, 'total_cost_usd', 0)
                print(f"\n💰 Turn 2 Cost: ${cost2:.4f}")
        
        # Execute visualization code
        print(f"\n🎨 Creating visualization...")
        
        viz_code_blocks = re.findall(r'```python\n(.*?)\n```', response2, re.DOTALL)
        chart_created = False
        
        if viz_code_blocks:
            viz_code = viz_code_blocks[0].strip()
            
            try:
                exec_globals = {'pd': pd, 'plt': plt, 'np': np}
                exec(viz_code, exec_globals)
                
                chart_path = Path('analytics_chart.png')
                if chart_path.exists():
                    logger.log_execution(viz_code, str(chart_path), turn=2, success=True)
                    print(f"✅ Chart created: {chart_path}")
                    chart_created = True
                else:
                    logger.log_execution(viz_code, None, turn=2, success=False, error="Chart file not found")
                    print("⚠️  Chart file not found after execution")
                    
            except Exception as e:
                logger.log_execution(viz_code, None, turn=2, success=False, error=str(e))
                print(f"❌ Visualization error: {e}")
        
        # TURN 3: Chart analysis (if successful)
        cost3 = 0
        if chart_created:
            print(f"\n\n🔍 TURN 3: Chart Analysis")
            print("-" * 40)
            
            # Read the chart image and include it in the query
            chart_path = Path('analytics_chart.png')
            chart_abs_path = chart_path.absolute()
            
            query3 = f"""I created a chart showing revenue by category with these values:
{revenue_dict if 'revenue_dict' in locals() else 'Electronics vs Accessories'}

Please analyze this chart image {chart_abs_path} and provide:
1. Key insights from the visualization
2. Which category performs better
3. Business recommendations based on the data shown"""
            
            print("Analyzing the generated chart...")
            # Claude will automatically read the image file mentioned in prompt
            logger.log_query(query3, turn=3, attachments=[str(chart_path)])
            await client.query(query3)
            
            async for message in client.receive_response():
                # Log the complete response object
                logger.log_response(message, turn=3)
                
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            print(block.text, end='', flush=True)
                
                if type(message).__name__ == "ResultMessage":
                    cost3 = getattr(message, 'total_cost_usd', 0)
                    print(f"\n💰 Turn 3 Cost: ${cost3:.4f}")
        
        # Final summary
        total_cost = cost1 + cost2 + cost3
        turns = 3 if chart_created else 2
        
        print(f"\n\n🎯 DEMO COMPLETE")
        print("="*50)
        print(f"✅ Turns completed: {turns}")
        print(f"💰 Total cost: ${total_cost:.4f}")
        print(f"🆔 Session: {session_id}")
        print(f"📊 Chart created: {'Yes' if chart_created else 'No'}")
        
        if chart_created:
            print(f"📁 Chart location: {Path('analytics_chart.png').absolute()}")
        
        final_result = {
            'success': True,
            'total_cost': total_cost,
            'session_id': session_id,
            'chart_created': chart_created,
            'turns': turns
        }
        
        # Close logging session
        logger.close_session(final_result)
        print(f"📝 Complete session log saved to: {logger.log_file}")
        
        return final_result


async def main():
    try:
        result = await working_demo()
        print(f"\n✅ Demo result: {result}")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())