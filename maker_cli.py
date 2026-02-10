#!/usr/bin/env python3
"""
MAKER Framework Interactive CLI

Simple interface for users to input their task and let MAKER handle the rest.
"""

import getpass
import os
import sys
from typing import Optional

from maker.openrouter import (
    OpenRouterClient,
    estimate_cost,
    format_cost_estimate,
    get_recommended_model,
    list_available_models
)
from maker.decomposer import TaskDecomposer
from maker.algorithms import estimate_kmin


def print_header():
    """Print CLI header."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                    MAKER Framework CLI                        ║
║   Maximal Agentic decomposition, first-to-ahead-by-K         ║
║          Error correction, and Red-flagging                   ║
╚═══════════════════════════════════════════════════════════════╝
""")


def get_api_key() -> Optional[str]:
    """Get OpenRouter API key from user or environment."""
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        print("\n⚠️  OpenRouter API key not found in environment.")
        print("You can get a free API key at: https://openrouter.ai/")
        print("\nOptions:")
        print("1. Set environment variable: export OPENROUTER_API_KEY='your-key'")
        print("2. Enter it now (not recommended for security)")
        
        choice = input("\nEnter API key now? (y/n): ").strip().lower()
        if choice == 'y':
            api_key = getpass.getpass("API Key: ").strip()
        else:
            print("\n❌ Cannot proceed without API key. Exiting.")
            return None
    
    return api_key


def get_task_input() -> tuple:
    """Get task description from user."""
    print("\n" + "="*70)
    print("STEP 1: Describe Your Task")
    print("="*70)
    
    print("\nWhat task would you like MAKER to solve?")
    print("(Be as specific as possible about what needs to be done)")
    print("\nExample: 'Solve the 15-disk Towers of Hanoi puzzle'")
    print("Example: 'Generate a 10-chapter novel outline with character arcs'")
    print("Example: 'Plan a 30-day marketing campaign with daily tasks'\n")
    
    task_description = input("Task: ").strip()
    
    if not task_description:
        print("❌ Task description cannot be empty.")
        return None, None
    
    print("\nWhat defines success for this task?")
    print("(Optional - press Enter to use default)\n")
    
    success_criteria = input("Success criteria: ").strip()
    if not success_criteria:
        success_criteria = "Task completed successfully with all requirements met"
    
    return task_description, success_criteria


def confirm_decomposition(decomposition: dict) -> bool:
    """Show decomposition and get user confirmation."""
    print("\n" + "="*70)
    print("STEP 2: Task Decomposition Analysis")
    print("="*70)
    
    print(f"\n📊 Estimated Steps: {decomposition['estimated_steps']:,}")
    print(f"📋 Step Types: {len(decomposition['step_types'])}")
    
    print("\n🔍 Step Type Breakdown:")
    for i, step_type in enumerate(decomposition['step_types'], 1):
        print(f"\n  {i}. {step_type['name']}")
        print(f"     {step_type['description']}")
        print(f"     Frequency: {step_type['frequency']}")
    
    print(f"\n📝 Execution Order:")
    print(f"   {decomposition['execution_order']}")
    
    print("\n" + "-"*70)
    choice = input("\nDoes this decomposition look correct? (y/n): ").strip().lower()
    return choice == 'y'


def show_cost_estimate(estimate: dict) -> bool:
    """Show cost estimate and get user confirmation."""
    print("\n" + "="*70)
    print("STEP 3: Cost Estimation")
    print("="*70)
    
    print(format_cost_estimate(estimate))
    
    if estimate['total_cost'] < 0.01:
        print("💰 This task will cost less than $0.01 to run!")
    elif estimate['total_cost'] < 0.10:
        print("💰 This is a very affordable task to run.")
    elif estimate['total_cost'] < 1.00:
        print("💵 This task has a reasonable cost.")
    else:
        print("💸 This is a larger task with higher costs.")
    
    print("\n" + "-"*70)
    choice = input("\nProceed with execution? (y/n): ").strip().lower()
    return choice == 'y'


def select_model() -> str:
    """Let user select a model or use recommended."""
    print("\n" + "="*70)
    print("Model Selection")
    print("="*70)
    
    recommended = get_recommended_model()
    
    print("\n1. Use recommended model (cheapest, most capable)")
    print("2. View all available models and choose")
    
    choice = input("\nChoice (1/2): ").strip()
    
    if choice == '2':
        print(list_available_models())
        model = input("Enter model ID: ").strip()
        return model
    else:
        print(f"\n✅ Using recommended model: {recommended}")
        return recommended


def main():
    """Main CLI entry point."""
    print_header()
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        return 1
    
    try:
        client = OpenRouterClient(api_key=api_key)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    # Get task input
    task_description, success_criteria = get_task_input()
    if not task_description:
        return 1
    
    print("\n🔄 Analyzing task and generating decomposition...")
    print("   (This may take a moment...)")
    
    # Decompose task
    try:
        decomposer = TaskDecomposer(client)
        decomposition = decomposer.decompose_task(task_description, success_criteria)
    except Exception as e:
        print(f"\n❌ Error during decomposition: {e}")
        return 1
    
    # Show decomposition and get confirmation
    if not confirm_decomposition(decomposition):
        print("\n❌ Task decomposition rejected. Exiting.")
        return 1
    
    # Estimate parameters
    estimated_steps, recommended_k = decomposer.estimate_parameters(decomposition)
    
    print(f"\n✅ Recommended voting parameter (k): {recommended_k}")
    
    # Select model
    model = select_model()
    
    # Estimate cost
    try:
        cost_estimate = estimate_cost(
            num_steps=estimated_steps,
            k=recommended_k,
            model=model
        )
    except Exception as e:
        print(f"\n❌ Error estimating cost: {e}")
        return 1
    
    # Show cost and get confirmation
    if not show_cost_estimate(cost_estimate):
        print("\n❌ Execution cancelled by user.")
        return 0
    
    # Save configuration
    print("\n" + "="*70)
    print("STEP 4: Saving Configuration")
    print("="*70)
    
    import json
    
    config = {
        'task_description': task_description,
        'success_criteria': success_criteria,
        'decomposition': decomposition,
        'model': model,
        'k': recommended_k,
        'estimated_steps': estimated_steps,
        'cost_estimate': cost_estimate
    }
    
    config_file = 'maker_task_config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to: {config_file}")
    
    print("\n" + "="*70)
    print("Next Steps")
    print("="*70)
    print("""
Your task has been analyzed and configured!

To execute the task, you have two options:

1. Use the generated configuration with the MAKER framework:
   python -m maker.execute maker_task_config.json

2. Implement custom logic using the decomposition:
   - Review the micro-agent prompts in the config file
   - Use the maker.algorithms module to implement execution
   - See examples/towers_of_hanoi/main.py for reference

The configuration file contains:
  ✓ Task decomposition
  ✓ Micro-agent prompts
  ✓ Recommended parameters
  ✓ Cost estimates

Happy building! 🚀
""")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
