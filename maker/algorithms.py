"""
Core MAKER Framework Algorithms

This module implements the three core algorithms of the MAKER framework:
1. generate_solution: Orchestrates the overall task
2. do_voting: Implements first-to-ahead-by-k voting
3. get_vote: Samples from the LLM with red-flagging

Based on the paper "Solving a Million-Step LLM Task with Zero Errors"
arXiv:2511.09030
"""

from typing import Callable, Any, Dict, List, Tuple, Optional
from collections import defaultdict


def generate_solution(
    initial_state: Any,
    model: Callable,
    k: int,
    num_steps: int,
    parse_action: Callable,
    parse_next_state: Callable,
    check_red_flags: Callable
) -> List[Any]:
    """
    Algorithm 1: generate_solution
    
    Orchestrates the overall task by iterating through all steps and
    applying the voting mechanism at each step.
    
    Args:
        initial_state: The initial state of the task
        model: A callable that takes a state and returns an LLM response
        k: The voting parameter (first-to-ahead-by-k)
        num_steps: Total number of steps in the task
        parse_action: Function to extract action from LLM response
        parse_next_state: Function to extract next state from LLM response
        check_red_flags: Function to check if response has red flags
        
    Returns:
        List of actions representing the complete solution
    """
    actions = []
    current_state = initial_state
    
    for step in range(num_steps):
        action, next_state = do_voting(
            current_state,
            model,
            k,
            parse_action,
            parse_next_state,
            check_red_flags
        )
        actions.append(action)
        current_state = next_state
        
    return actions


def do_voting(
    state: Any,
    model: Callable,
    k: int,
    parse_action: Callable,
    parse_next_state: Callable,
    check_red_flags: Callable
) -> Tuple[Any, Any]:
    """
    Algorithm 2: do_voting
    
    Implements the first-to-ahead-by-k voting mechanism.
    Continues sampling until one candidate has k more votes than any other.
    
    Args:
        state: The current state
        model: A callable that takes a state and returns an LLM response
        k: The voting parameter
        parse_action: Function to extract action from LLM response
        parse_next_state: Function to extract next state from LLM response
        check_red_flags: Function to check if response has red flags
        
    Returns:
        Tuple of (winning_action, next_state)
    """
    vote_counts = defaultdict(int)
    
    while True:
        action, next_state = get_vote(
            state,
            model,
            parse_action,
            parse_next_state,
            check_red_flags
        )
        
        # Convert action to a hashable type for counting
        # (assumes action can be converted to tuple or is already hashable)
        action_key = tuple(action) if isinstance(action, list) else action
        vote_counts[action_key] += 1
        
        # Check if we have a winner (first-to-ahead-by-k)
        max_votes = max(vote_counts.values())
        second_max_votes = sorted(vote_counts.values(), reverse=True)[1] if len(vote_counts) > 1 else 0
        
        if max_votes >= k + second_max_votes:
            # Find the winning action
            for candidate_action, votes in vote_counts.items():
                if votes == max_votes:
                    # Convert back to list if needed
                    winning_action = list(candidate_action) if isinstance(candidate_action, tuple) else candidate_action
                    return winning_action, next_state


def get_vote(
    state: Any,
    model: Callable,
    parse_action: Callable,
    parse_next_state: Callable,
    check_red_flags: Callable
) -> Tuple[Any, Any]:
    """
    Algorithm 3: get_vote
    
    Samples a response from the model and checks for red flags.
    If red flags are detected, resamples until a valid response is obtained.
    
    Args:
        state: The current state
        model: A callable that takes a state and returns an LLM response
        parse_action: Function to extract action from LLM response
        parse_next_state: Function to extract next state from LLM response
        check_red_flags: Function to check if response has red flags
        
    Returns:
        Tuple of (action, next_state)
    """
    while True:
        response = model(state)
        
        if not check_red_flags(response):
            # No red flags detected, parse and return
            action = parse_action(response)
            next_state = parse_next_state(response)
            return action, next_state
        # If red flags detected, loop continues and resamples


def create_red_flag_checker(
    max_tokens: Optional[int] = None,
    required_format_validator: Optional[Callable] = None
) -> Callable:
    """
    Factory function to create a red-flag checking function.
    
    Args:
        max_tokens: Maximum allowed token count (approximate by word count)
        required_format_validator: Function that returns True if format is valid
        
    Returns:
        A function that checks for red flags in responses
    """
    def check_red_flags(response: str) -> bool:
        """
        Returns True if red flags are detected, False otherwise.
        """
        # Check for overly long responses
        if max_tokens is not None:
            # Approximate token count by word count (rough estimate)
            word_count = len(response.split())
            if word_count > max_tokens:
                return True
        
        # Check for format violations
        if required_format_validator is not None:
            if not required_format_validator(response):
                return True
        
        return False
    
    return check_red_flags


def estimate_kmin(num_steps: int, per_step_success_rate: float, target_success_rate: float = 0.9) -> int:
    """
    Estimate the minimum k value needed to achieve target success rate.
    
    Based on Equation 14 from the paper:
    k_min = ln(t^(-m/s) - 1) / ln((1-p)/p)
    
    For maximal decomposition (m=1):
    k_min = ln(t^(-1/s) - 1) / ln((1-p)/p)
    
    Args:
        num_steps: Total number of steps in the task
        per_step_success_rate: Success rate for a single step (p)
        target_success_rate: Desired overall success rate (t)
        
    Returns:
        Estimated minimum k value
    """
    import math
    
    p = per_step_success_rate
    t = target_success_rate
    s = num_steps
    
    # For maximal decomposition (m=1)
    numerator = math.log(t ** (-1/s) - 1)
    denominator = math.log((1 - p) / p)
    
    k_min = numerator / denominator
    
    # Round up to nearest integer
    return math.ceil(k_min)
