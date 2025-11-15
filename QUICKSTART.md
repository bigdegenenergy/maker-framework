# MAKER Framework - Quick Start Guide

Get started with MAKER in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/bigdegenenergy/maker-framework.git
cd maker-framework

# Install dependencies
pip install -r requirements.txt
```

## Get Your API Key

1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Set it as an environment variable:

```bash
export OPENROUTER_API_KEY='your-key-here'
```

**Why OpenRouter?**
- Access to 50+ models from one API
- Pay only for what you use
- Automatic selection of cheapest capable model
- Free tier available

## Run the Interactive CLI

```bash
python maker_cli.py
```

The CLI will guide you through:

1. **Describing your task** - Just explain what you want to accomplish
2. **Reviewing the decomposition** - See how MAKER breaks it down
3. **Viewing cost estimate** - Know exactly what it will cost
4. **Confirming execution** - Proceed only if you're happy

## Example Session

```
╔═══════════════════════════════════════════════════════════════╗
║                    MAKER Framework CLI                        ║
╚═══════════════════════════════════════════════════════════════╝

STEP 1: Describe Your Task
======================================================================

Task: Create a 7-day meal plan with recipes and shopping list

🔄 Analyzing task and generating decomposition...

STEP 2: Task Decomposition Analysis
======================================================================

📊 Estimated Steps: 21
📋 Step Types: 3

1. Generate daily meal ideas
   Frequency: 7 times (once per day)

2. Create detailed recipes
   Frequency: 21 times (3 meals × 7 days)

3. Compile shopping list
   Frequency: 1 time (final step)

Does this decomposition look correct? (y/n): y

STEP 3: Cost Estimation
======================================================================

Model: Google Gemini 2.0 Flash
Steps: 21
Voting Parameter (k): 2

Estimated LLM Calls: 63
Input Tokens: 31,500
Output Tokens: 6,300

Cost Breakdown:
  Input:  $0.0000
  Output: $0.0000
  ----------------------------------------
  TOTAL:  $0.0003

💰 This task will cost less than $0.01 to run!

Proceed with execution? (y/n): y

✅ Configuration saved to: maker_task_config.json
```

## What You Get

After running the CLI, you'll have:

- ✅ **maker_task_config.json** - Complete task configuration
- ✅ **Micro-agent prompts** - Ready to use
- ✅ **Cost estimate** - Exact pricing
- ✅ **Recommended parameters** - Optimized k value

## Next Steps

### Option 1: Use the Configuration

```python
import json
from maker import OpenRouterClient, generate_solution

# Load configuration
with open('maker_task_config.json') as f:
    config = json.load(f)

# Initialize client
client = OpenRouterClient()

# Implement your execution logic using the decomposition
# See examples/towers_of_hanoi/main.py for reference
```

### Option 2: Study the Example

```bash
# Run the Towers of Hanoi example
python examples/towers_of_hanoi/main.py
```

### Option 3: Read the Docs

- **Comprehensive Guide**: `docs/MAKER_Framework_Guide.md`
- **Detailed Usage**: `docs/USAGE.md`

## Common Tasks & Costs

| Task Type | Estimated Steps | Estimated Cost |
|-----------|----------------|----------------|
| 7-day meal plan | 20-30 | < $0.01 |
| 30-day content calendar | 100-150 | $0.01-0.05 |
| Novel outline (10 chapters) | 50-100 | $0.01-0.03 |
| Project plan (50 tasks) | 50-100 | $0.01-0.03 |
| 10-disk Towers of Hanoi | 1,023 | $0.001 |
| 20-disk Towers of Hanoi | 1,048,575 | $0.65 |

*Costs using Google Gemini 2.0 Flash (recommended model)*

## Tips for Success

1. **Be specific** - The more detailed your task description, the better the decomposition
2. **Review carefully** - Check the decomposition before proceeding
3. **Start small** - Test with a smaller version of your task first
4. **Iterate** - Refine your task description if the decomposition isn't quite right

## Troubleshooting

### "API key not found"
```bash
export OPENROUTER_API_KEY='your-key-here'
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Decomposition doesn't look right"
- Try being more specific in your task description
- Add more details about success criteria
- Break your task into smaller sub-tasks

## Get Help

- 📖 Read the full guide: `docs/MAKER_Framework_Guide.md`
- 💬 Open an issue: [GitHub Issues](https://github.com/bigdegenenergy/maker-framework/issues)
- 📝 Check examples: `examples/towers_of_hanoi/`

---

Ready to solve complex tasks with zero errors? Run `python maker_cli.py` now! 🚀
