# MAKER Framework Usage Guide

This guide provides step-by-step instructions for using the MAKER framework in your own projects.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/maker_framework.git
   cd maker_framework
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Quick Start: Running the Example

The Towers of Hanoi example demonstrates the MAKER framework in action:

```bash
python examples/towers_of_hanoi/main.py
```

This will solve a 3-disk Towers of Hanoi puzzle using the MAKER framework with k=3 voting.

## Adapting to Your Own Task

### Step 1: Define Your Task

Start by clearly defining your task:
- What is the overall goal?
- How many steps are involved?
- What does each step look like?

### Step 2: Create Micro-agent Prompts

Create a prompts module for your task (similar to `examples/towers_of_hanoi/prompts.py`):

```python
def create_microagent_prompt(state: dict) -> str:
    """
    Create a prompt for your micro-agent.
    
    The prompt should:
    - Provide the current state
    - Clearly define the single step to perform
    - Specify the exact output format
    """
    prompt = f"""You are a focused micro-agent.
    
Current State: {state}

Your Task: [Define the single step]

Output Format: [Specify exact format, preferably JSON]
"""
    return prompt
```

### Step 3: Implement Parsing Functions

Create functions to parse the LLM's responses:

```python
def parse_action(response: str):
    """Extract the action from the response."""
    # Parse the response and extract the action
    pass

def parse_next_state(response: str):
    """Extract or compute the next state from the response."""
    # Parse the response and determine the next state
    pass
```

### Step 4: Configure Red-Flagging

Define what constitutes a "red flag" for your task:

```python
from maker import create_red_flag_checker

def validate_format(response: str) -> bool:
    """Check if response matches expected format."""
    # Return True if valid, False if invalid
    pass

red_flag_checker = create_red_flag_checker(
    max_tokens=500,  # Adjust based on your task
    required_format_validator=validate_format
)
```

### Step 5: Set Up the Model Caller

Create a function that calls your LLM:

```python
from openai import OpenAI

client = OpenAI()

def call_model(state):
    """Call the LLM with the current state."""
    prompt = create_microagent_prompt(state)
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a precise micro-agent."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content
```

### Step 6: Use the MAKER Framework

Put it all together using the MAKER algorithms:

```python
from maker import generate_solution, estimate_kmin

# Estimate the minimum k value
num_steps = 1000  # Your task's step count
k = estimate_kmin(num_steps, per_step_success_rate=0.99)

# Solve the task
solution = generate_solution(
    initial_state=your_initial_state,
    model=call_model,
    k=k,
    num_steps=num_steps,
    parse_action=parse_action,
    parse_next_state=parse_next_state,
    check_red_flags=red_flag_checker
)
```

## Advanced Configuration

### Adjusting the Voting Parameter (k)

The voting parameter k controls the trade-off between accuracy and cost:

- **Lower k (e.g., k=2)**: Faster, cheaper, but less reliable
- **Higher k (e.g., k=5)**: Slower, more expensive, but more reliable

Use `estimate_kmin()` to calculate the minimum k for your desired success rate:

```python
from maker import estimate_kmin

k = estimate_kmin(
    num_steps=1000000,
    per_step_success_rate=0.99,
    target_success_rate=0.9
)
```

### Custom Red-Flagging Criteria

You can add custom red-flagging logic beyond length and format:

```python
def check_red_flags(response: str) -> bool:
    """Returns True if red flags detected."""
    
    # Check length
    if len(response.split()) > 500:
        return True
    
    # Check format
    if not validate_format(response):
        return True
    
    # Custom checks
    if "I don't know" in response.lower():
        return True
    
    if "error" in response.lower():
        return True
    
    return False
```

### Using Different Models

The framework works with any LLM that can be called via a function. To use a different model:

```python
def call_model(state):
    # Use any LLM API
    response = your_llm_api.generate(
        prompt=create_microagent_prompt(state)
    )
    return response
```

## Best Practices

1. **Start Small**: Test your implementation on a small version of your task first (e.g., 10-100 steps).

2. **Monitor Performance**: Track metrics like:
   - Average votes needed per step
   - Red-flag rate
   - Time per step

3. **Iterate on Prompts**: The quality of your micro-agent prompts significantly impacts success rate. Iterate and refine.

4. **Use Appropriate Models**: The paper shows that smaller, cheaper models work well with MAKER. Don't assume you need the largest model.

5. **Log Everything**: Keep detailed logs of responses, votes, and red flags for debugging and analysis.

## Troubleshooting

### High Red-Flag Rate

If many responses are being flagged:
- Your prompts may be unclear
- The max_tokens threshold may be too low
- The format validator may be too strict

### Slow Convergence in Voting

If steps require many votes to resolve:
- Your per-step success rate may be lower than expected
- Consider increasing k
- Review your prompts for clarity

### Inconsistent Results

If different runs produce different solutions:
- This may be expected for tasks with multiple valid solutions
- For deterministic tasks, check that your parsing is consistent
- Ensure your state representation is complete

## Further Reading

- See `docs/MAKER_Framework_Guide.md` for the full theoretical background
- Review the Towers of Hanoi example for a complete implementation
- Read the original paper: [arXiv:2511.09030](https://arxiv.org/abs/2511.09030)
