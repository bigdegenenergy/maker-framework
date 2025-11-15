"""
Prompts for the Towers of Hanoi example

This module defines the micro-agent prompts used in the Towers of Hanoi
implementation of the MAKER framework.
"""


def create_move_prompt(state: dict) -> str:
    """
    Create a prompt for the micro-agent to determine the next move.
    
    Args:
        state: Dictionary containing:
            - pegs: List of three lists, each representing a peg with disks
            - goal: The target peg (usually 2)
            - num_disks: Total number of disks
            
    Returns:
        A formatted prompt string
    """
    pegs = state['pegs']
    goal = state.get('goal', 2)
    num_disks = state['num_disks']
    
    prompt = f"""You are a Towers of Hanoi expert. Your task is to determine the next single move.

**Current State:**
Peg 0: {pegs[0] if pegs[0] else 'empty'}
Peg 1: {pegs[1] if pegs[1] else 'empty'}
Peg 2: {pegs[2] if pegs[2] else 'empty'}

**Goal:** Move all {num_disks} disks to Peg {goal}

**Rules:**
1. Only move one disk at a time
2. A larger disk cannot be placed on top of a smaller disk
3. Only the top disk of each peg can be moved

**Your Task:**
Determine the next optimal move that progresses toward the goal.

**Output Format:**
Respond with ONLY a JSON object in this exact format:
{{"disk": <disk_number>, "from": <source_peg>, "to": <destination_peg>}}

Example: {{"disk": 1, "from": 0, "to": 2}}

Do not include any explanation or additional text. Only output the JSON object.
"""
    
    return prompt


def create_system_prompt() -> str:
    """
    Create the system prompt for the Towers of Hanoi micro-agent.
    
    Returns:
        A system prompt string
    """
    return """You are a precise, focused micro-agent specialized in determining single moves in the Towers of Hanoi puzzle. 
You always respond with valid JSON in the exact format requested, with no additional text or explanation.
You are highly reliable and never make illegal moves."""
