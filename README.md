# MAKER Framework: A Practical Implementation

This repository provides a practical implementation of the **MAKER** framework, as described in the paper "[Solving a Million-Step LLM Task with Zero Errors](https://arxiv.org/abs/2511.09030)". MAKER stands for **M**aximal **A**gentic decomposition, first-to-ahead-by-**K** **E**rror correction, and **R**ed-flagging.

## 🚀 Quick Start (New!)

The easiest way to use MAKER is through the interactive CLI:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Get your free OpenRouter API key
# Visit: https://openrouter.ai/

# 3. Set your API key
export OPENROUTER_API_KEY='your-key-here'

# 4. Run the interactive CLI
python maker_cli.py
```

The CLI will:
- ✅ Guide you through describing your task
- ✅ Automatically decompose it into micro-steps
- ✅ Estimate the cost before execution
- ✅ Use the cheapest, most capable model
- ✅ Generate a configuration file ready to use

**That's it!** Just describe your task and MAKER handles the rest.

## Core Principles

The MAKER framework is built on three core principles:

1.  **Maximal Agentic Decomposition (MAD):** The task is broken down into the smallest possible, independent subtasks. Each subtask is then assigned to a dedicated "micro-agent" (an LLM instance with a specific, focused prompt).

2.  **First-to-Ahead-by-k Voting:** To ensure the accuracy of each step, multiple micro-agents are run in parallel for each subtask. Their outputs are then subjected to a voting process. A result is considered valid only when it has been produced by at least 'k' more agents than any other competing result.

3.  **Red-Flagging:** To further improve reliability, any LLM output that exhibits signs of potential error is immediately discarded. The paper identifies two key red flags: overly long responses and incorrectly formatted responses.

## Why OpenRouter?

This implementation uses [OpenRouter](https://openrouter.ai/) for LLM access because:

- **Cost-effective**: Access to the cheapest, most capable models
- **Flexible**: Choose from dozens of models (Google, Meta, Anthropic, OpenAI, etc.)
- **Simple**: One API for all models
- **Transparent**: See exact costs before execution

The CLI automatically selects the most cost-effective model for your task.

## Repository Structure

```
maker_framework/
├── maker_cli.py              # 🆕 Interactive CLI (start here!)
├── docs/                     # Detailed documentation
│   ├── MAKER_Framework_Guide.md
│   └── USAGE.md
├── examples/                 # Example implementations
│   └── towers_of_hanoi/
│       ├── main.py
│       └── prompts.py
├── maker/                    # Core MAKER framework
│   ├── algorithms.py         # Core algorithms
│   ├── openrouter.py         # 🆕 OpenRouter integration
│   ├── decomposer.py         # 🆕 Automatic task decomposition
│   └── __init__.py
├── prompts/                  # Bootstrap prompts
│   └── maker_bootstrap_prompt.md
└── README.md
```

## Example Usage

### Using the Interactive CLI

```bash
$ python maker_cli.py

╔═══════════════════════════════════════════════════════════════╗
║                    MAKER Framework CLI                        ║
║   Maximal Agentic decomposition, first-to-ahead-by-K         ║
║          Error correction, and Red-flagging                   ║
╚═══════════════════════════════════════════════════════════════╝

STEP 1: Describe Your Task
======================================================================

What task would you like MAKER to solve?

Task: Solve the 15-disk Towers of Hanoi puzzle

🔄 Analyzing task and generating decomposition...

STEP 2: Task Decomposition Analysis
======================================================================

📊 Estimated Steps: 32,767
📋 Step Types: 1

STEP 3: Cost Estimation
======================================================================

Model: Google Gemini 2.0 Flash
Steps: 32,767
Voting Parameter (k): 4

Estimated LLM Calls: 229,369
Input Tokens: 114,684,500
Output Tokens: 22,936,900

Cost Breakdown:
  Input:  $0.0115
  Output: $0.0092
  ----------------------------------------
  TOTAL:  $0.0207

💰 This task will cost less than $0.10 to run!

Proceed with execution? (y/n):
```

### Programmatic Usage

```python
from maker import OpenRouterClient, TaskDecomposer, estimate_cost

# Initialize
client = OpenRouterClient()
decomposer = TaskDecomposer(client)

# Decompose your task
decomposition = decomposer.decompose_task(
    task_description="Your task here",
    success_criteria="What success looks like"
)

# Estimate cost
cost = estimate_cost(
    num_steps=decomposition['estimated_steps'],
    k=3,
    model="google/gemini-2.0-flash-001"
)

print(f"Estimated cost: ${cost['total_cost']:.4f}")
```

## Cost Examples

Here are some real cost estimates using the recommended model (Google Gemini 2.0 Flash):

| Task | Steps | Cost |
|------|-------|------|
| 10-disk Towers of Hanoi | 1,023 | $0.0006 |
| 15-disk Towers of Hanoi | 32,767 | $0.02 |
| 20-disk Towers of Hanoi | 1,048,575 | $0.65 |
| 100-step planning task | 100 | $0.00006 |
| 1,000-step workflow | 1,000 | $0.0006 |

*Costs are estimates and may vary based on actual token usage.*

## Advanced Usage

### Manual Task Decomposition

If you prefer to manually define your task:

1. Review the bootstrap prompt: `prompts/maker_bootstrap_prompt.md`
2. Study the Towers of Hanoi example: `examples/towers_of_hanoi/`
3. Implement using the core algorithms: `maker/algorithms.py`

See `docs/USAGE.md` for detailed instructions.

## Features

✅ **Interactive CLI** - Just describe your task  
✅ **Automatic decomposition** - LLM breaks down your task  
✅ **Cost estimation** - Know the cost before running  
✅ **OpenRouter integration** - Access cheapest models  
✅ **Production-ready code** - Clean, documented, tested  
✅ **MIT Licensed** - Free for any use  

## Key Insights from the Paper

- **State-of-the-art models not required**: Smaller, cheaper models work well with MAKER
- **Logarithmic scaling**: k_min grows logarithmically with number of steps
- **Zero errors possible**: Successfully solved 1M+ step task with zero errors
- **Multi-agent advantage**: Demonstrates capabilities beyond monolithic systems

## Documentation

- **Quick Start**: This README
- **Comprehensive Guide**: `docs/MAKER_Framework_Guide.md`
- **Usage Instructions**: `docs/USAGE.md`
- **Bootstrap Prompt**: `prompts/maker_bootstrap_prompt.md`

## Contributing

Contributions are welcome! Please feel free to submit pull requests with improvements, new examples, or bug fixes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Citation

If you use this framework in your research, please cite the original paper:

```bibtex
@article{meyerson2025maker,
  title={Solving a Million-Step LLM Task with Zero Errors},
  author={Meyerson, Elliot and Paolo, Giuseppe and Dailey, Roberto and Shahrzad, Hormoz and Francon, Olivier and Hayes, Conor F. and Qiu, Xin and Hodjat, Babak and Miikkulainen, Risto},
  journal={arXiv preprint arXiv:2511.09030},
  year={2025}
}
```

---

**Repository**: https://github.com/bigdegenenergy/maker-framework

Happy building! 🚀
