# Claude Code SDK - Data Analytics Multi-Turn Demo

This demonstrates the Claude Code SDK's multi-turn agent workflow for data analytics with proper result passing between turns.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your API key:**
   ```bash
   # Create .env file with your key
   echo "ANTHROPIC_API_KEY=your_key_here" > .env
   ```

3. **Run the demo:**
   ```bash
   python claude_code_demo.py
   ```

## 📊 What This Demo Shows

### **Multi-Turn Workflow:**
1. **Turn 1:** Data Analysis
   - Claude generates Python code to analyze `sample_data.csv`
   - Code is executed locally, results captured
   
2. **Turn 2:** Visualization  
   - **Key Feature:** Actual execution results are passed to Claude
   - Claude generates chart code using the real data
   - Chart created and saved as `analytics_chart.png`

3. **Turn 3:** Image Analysis
   - Chart image is sent to Claude for analysis
   - Claude provides business insights and recommendations

### **Key Features Demonstrated:**

✅ **Proper Result Passing** - Execution results sent to next turn  
✅ **Code Generation & Execution** - Real Python code generated and run  
✅ **Image Attachment** - Charts analyzed by Claude  
✅ **Session Persistence** - Context maintained across turns  
✅ **Cost Tracking** - Total API costs reported (~$0.08 for full workflow)  

## 📁 Files

- `claude_code_demo.py` - Main demo script (the working one!)
- `sample_data.csv` - Mock sales data for analysis
- `requirements.txt` - Python dependencies
- `.env` - API key configuration (create this)
- `.gitignore` - Git ignore rules

## 🔧 How It Works

The critical insight is that **Claude's session context remembers conversations but NOT local code execution results**. You must explicitly pass execution results back to Claude:

```python
# ❌ Wrong: Claude doesn't see execution results
query2 = "Based on previous analysis, create a chart"

# ✅ Correct: Pass actual results 
query2 = f"""Here are the ACTUAL results from execution:
{json.dumps(execution_results, indent=2)}
Now create a chart using these exact values."""
```

## 💰 Cost Example

Recent run:
- Turn 1 (Data Analysis): $0.011
- Turn 2 (Visualization): $0.026  
- Turn 3 (Image Analysis): $0.050
- **Total: $0.087**

## 🎯 Perfect For

- Learning Claude Code SDK multi-turn patterns
- Data analytics workflow prototyping  
- Understanding result passing between turns
- Image analysis integration

Run the demo to see the complete workflow in action!