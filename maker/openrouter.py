"""
OpenRouter Integration for MAKER Framework

Provides cost-effective LLM access through OpenRouter with cost estimation.
"""

import os
from typing import Dict, List, Optional, Tuple
import requests


# OpenRouter pricing (per 1M tokens) - Updated regularly
OPENROUTER_MODELS = {
    "google/gemini-2.0-flash-001": {
        "name": "Google Gemini 2.0 Flash",
        "input_price": 0.10,  # per 1M tokens
        "output_price": 0.40,  # per 1M tokens
        "context_window": 1048576,
        "recommended": True
    },
    "meta-llama/llama-3.1-8b-instruct": {
        "name": "Meta Llama 3.1 8B",
        "input_price": 0.05,
        "output_price": 0.05,
        "context_window": 131072,
        "recommended": True
    },
    "anthropic/claude-3.5-sonnet": {
        "name": "Claude 3.5 Sonnet",
        "input_price": 3.00,
        "output_price": 15.00,
        "context_window": 200000,
        "recommended": False
    },
    "openai/gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "input_price": 0.15,
        "output_price": 0.60,
        "context_window": 128000,
        "recommended": True
    },
}


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided. Set OPENROUTER_API_KEY environment variable.")
        
        self.base_url = "https://openrouter.ai/api/v1"
    
    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Call OpenRouter chat completion API.
        
        Args:
            model: Model identifier (e.g., "google/gemini-2.0-flash-001")
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        response.raise_for_status()
        result = response.json()
        
        return result['choices'][0]['message']['content']


def estimate_cost(
    num_steps: int,
    k: int,
    model: str,
    avg_prompt_tokens: int = 500,
    avg_response_tokens: int = 100,
    red_flag_rate: float = 0.1
) -> Dict[str, float]:
    """
    Estimate the cost of running a MAKER task.
    
    Args:
        num_steps: Total number of steps in the task
        k: Voting parameter
        model: Model identifier
        avg_prompt_tokens: Average tokens per prompt
        avg_response_tokens: Average tokens per response
        red_flag_rate: Estimated rate of red-flagged responses (0.0-1.0)
        
    Returns:
        Dictionary with cost breakdown
    """
    if model not in OPENROUTER_MODELS:
        raise ValueError(f"Unknown model: {model}")
    
    model_info = OPENROUTER_MODELS[model]
    
    # Estimate number of LLM calls needed
    # For first-to-ahead-by-k, we need approximately 2k-1 calls per step on average
    # Plus additional calls for red-flagged responses
    avg_calls_per_step = (2 * k - 1) * (1 + red_flag_rate)
    total_calls = num_steps * avg_calls_per_step
    
    # Calculate token usage
    total_input_tokens = total_calls * avg_prompt_tokens
    total_output_tokens = total_calls * avg_response_tokens
    
    # Calculate costs (prices are per 1M tokens)
    input_cost = (total_input_tokens / 1_000_000) * model_info['input_price']
    output_cost = (total_output_tokens / 1_000_000) * model_info['output_price']
    total_cost = input_cost + output_cost
    
    return {
        'model': model_info['name'],
        'num_steps': num_steps,
        'k': k,
        'estimated_calls': int(total_calls),
        'input_tokens': int(total_input_tokens),
        'output_tokens': int(total_output_tokens),
        'input_cost': input_cost,
        'output_cost': output_cost,
        'total_cost': total_cost
    }


def get_recommended_model() -> str:
    """
    Get the recommended (cheapest capable) model for MAKER tasks.
    
    Returns:
        Model identifier
    """
    recommended = [
        model_id for model_id, info in OPENROUTER_MODELS.items()
        if info.get('recommended', False)
    ]
    
    # Sort by total cost (input + output)
    recommended.sort(
        key=lambda m: OPENROUTER_MODELS[m]['input_price'] + OPENROUTER_MODELS[m]['output_price']
    )
    
    return recommended[0] if recommended else list(OPENROUTER_MODELS.keys())[0]


def format_cost_estimate(estimate: Dict) -> str:
    """
    Format cost estimate for display.
    
    Args:
        estimate: Cost estimate dictionary from estimate_cost()
        
    Returns:
        Formatted string
    """
    return f"""
Cost Estimate for MAKER Task
{'='*50}
Model: {estimate['model']}
Steps: {estimate['num_steps']:,}
Voting Parameter (k): {estimate['k']}

Estimated LLM Calls: {estimate['estimated_calls']:,}
Input Tokens: {estimate['input_tokens']:,}
Output Tokens: {estimate['output_tokens']:,}

Cost Breakdown:
  Input:  ${estimate['input_cost']:.4f}
  Output: ${estimate['output_cost']:.4f}
  ----------------------------------------
  TOTAL:  ${estimate['total_cost']:.4f}
"""


def list_available_models() -> str:
    """
    List all available models with pricing.
    
    Returns:
        Formatted string with model information
    """
    output = "\nAvailable OpenRouter Models:\n"
    output += "=" * 80 + "\n\n"
    
    for model_id, info in OPENROUTER_MODELS.items():
        recommended = " [RECOMMENDED]" if info.get('recommended', False) else ""
        output += f"{info['name']}{recommended}\n"
        output += f"  ID: {model_id}\n"
        output += f"  Input:  ${info['input_price']:.2f} / 1M tokens\n"
        output += f"  Output: ${info['output_price']:.2f} / 1M tokens\n"
        output += f"  Context: {info['context_window']:,} tokens\n"
        output += "\n"
    
    return output
