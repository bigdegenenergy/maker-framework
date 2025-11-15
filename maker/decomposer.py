"""
Automatic Task Decomposition for MAKER Framework

Uses an LLM to automatically decompose tasks into micro-steps and generate prompts.
"""

import json
from typing import Dict, List, Tuple
from .openrouter import OpenRouterClient


DECOMPOSITION_SYSTEM_PROMPT = """You are an expert at breaking down complex tasks into the smallest possible atomic steps for execution by micro-agents in the MAKER framework.

Your goal is to decompose tasks following the principle of Maximal Agentic Decomposition (MAD), where each step should be:
1. As small and focused as possible
2. Independently executable
3. Have a clear input and output
4. Be verifiable

You will also generate focused micro-agent prompts for each step type."""


DECOMPOSITION_PROMPT_TEMPLATE = """Analyze the following task and decompose it into the smallest possible atomic steps:

**Task Description:**
{task_description}

**Success Criteria:**
{success_criteria}

Please provide:
1. The total estimated number of steps required
2. A breakdown of the different types of steps (there may be only one type, or several)
3. For each step type, a focused micro-agent prompt template

Respond with a JSON object in this exact format:
{{
  "estimated_steps": <number>,
  "step_types": [
    {{
      "name": "<step_type_name>",
      "description": "<what this step does>",
      "frequency": "<how often this step occurs>",
      "micro_agent_prompt": "<the prompt template for this step type>",
      "output_format": "<expected output format, preferably JSON>",
      "red_flag_indicators": ["<indicator1>", "<indicator2>"]
    }}
  ],
  "execution_order": "<description of how steps are sequenced>",
  "state_representation": "<how to represent state between steps>"
}}

Be specific and practical. The micro-agent prompts should be clear, focused, and include the exact output format expected."""


class TaskDecomposer:
    """Automatically decompose tasks using an LLM."""
    
    def __init__(self, client: OpenRouterClient, model: str = None):
        """
        Initialize task decomposer.
        
        Args:
            client: OpenRouter client instance
            model: Model to use for decomposition (defaults to recommended)
        """
        self.client = client
        self.model = model or "google/gemini-2.0-flash-001"
    
    def decompose_task(
        self,
        task_description: str,
        success_criteria: str = "Task completed successfully"
    ) -> Dict:
        """
        Decompose a task into micro-steps and generate prompts.
        
        Args:
            task_description: Description of the task to decompose
            success_criteria: What constitutes successful completion
            
        Returns:
            Dictionary with decomposition details
        """
        prompt = DECOMPOSITION_PROMPT_TEMPLATE.format(
            task_description=task_description,
            success_criteria=success_criteria
        )
        
        messages = [
            {"role": "system", "content": DECOMPOSITION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat_completion(
            model=self.model,
            messages=messages,
            temperature=0.3,  # Lower temperature for more consistent decomposition
            max_tokens=2000
        )
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            
            decomposition = json.loads(response_clean.strip())
            return decomposition
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse decomposition response: {e}\nResponse: {response}")
    
    def estimate_parameters(self, decomposition: Dict) -> Tuple[int, int]:
        """
        Estimate optimal parameters based on decomposition.
        
        Args:
            decomposition: Task decomposition dictionary
            
        Returns:
            Tuple of (estimated_steps, recommended_k)
        """
        estimated_steps = decomposition.get('estimated_steps', 100)
        
        # Recommend k based on task size
        if estimated_steps < 100:
            recommended_k = 2
        elif estimated_steps < 1000:
            recommended_k = 3
        elif estimated_steps < 10000:
            recommended_k = 4
        else:
            recommended_k = 5
        
        return estimated_steps, recommended_k
    
    def generate_implementation_guide(self, decomposition: Dict) -> str:
        """
        Generate a human-readable implementation guide.
        
        Args:
            decomposition: Task decomposition dictionary
            
        Returns:
            Formatted guide string
        """
        guide = f"""
Task Decomposition Analysis
{'='*80}

Estimated Total Steps: {decomposition['estimated_steps']:,}

Step Types:
"""
        for i, step_type in enumerate(decomposition['step_types'], 1):
            guide += f"""
{i}. {step_type['name']}
   Description: {step_type['description']}
   Frequency: {step_type['frequency']}
   
   Micro-agent Prompt:
   {'-'*70}
{step_type['micro_agent_prompt']}
   {'-'*70}
   
   Expected Output Format:
   {step_type['output_format']}
   
   Red Flag Indicators:
   {', '.join(step_type['red_flag_indicators'])}

"""
        
        guide += f"""
Execution Order:
{decomposition['execution_order']}

State Representation:
{decomposition['state_representation']}
"""
        
        return guide


def create_micro_agent_from_decomposition(
    step_type: Dict,
    client: OpenRouterClient,
    model: str
) -> callable:
    """
    Create a micro-agent function from a step type definition.
    
    Args:
        step_type: Step type dictionary from decomposition
        client: OpenRouter client
        model: Model to use
        
    Returns:
        Callable micro-agent function
    """
    def micro_agent(state: Dict) -> str:
        """Generated micro-agent function."""
        # Format the prompt with current state
        prompt = step_type['micro_agent_prompt']
        
        # Replace state placeholders
        for key, value in state.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))
        
        messages = [
            {"role": "system", "content": "You are a focused micro-agent. Respond only with the requested output format, no additional text."},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat_completion(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response
    
    return micro_agent
