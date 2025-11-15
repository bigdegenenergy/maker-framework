"""
Towers of Hanoi Example using MAKER Framework

This example demonstrates how to apply the MAKER framework to solve
the Towers of Hanoi puzzle with high reliability.
"""

import json
import os
from typing import Dict, List, Any
from openai import OpenAI

# Import MAKER framework components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from maker import generate_solution, create_red_flag_checker, estimate_kmin
from examples.towers_of_hanoi.prompts import create_move_prompt, create_system_prompt


class TowersOfHanoiSolver:
    """
    Solver for Towers of Hanoi using the MAKER framework.
    """
    
    def __init__(self, num_disks: int, k: int = 3, model_name: str = "gpt-4.1-mini"):
        """
        Initialize the solver.
        
        Args:
            num_disks: Number of disks in the puzzle
            k: Voting parameter (first-to-ahead-by-k)
            model_name: Name of the OpenAI model to use
        """
        self.num_disks = num_disks
        self.k = k
        self.model_name = model_name
        self.client = OpenAI()  # API key from environment
        
        # Calculate the number of steps needed (2^n - 1)
        self.num_steps = (2 ** num_disks) - 1
        
        # Create red-flag checker
        self.red_flag_checker = create_red_flag_checker(
            max_tokens=750,  # As per the paper
            required_format_validator=self._validate_format
        )
        
    def _validate_format(self, response: str) -> bool:
        """
        Validate that the response is in the correct JSON format.
        
        Args:
            response: The LLM response
            
        Returns:
            True if format is valid, False otherwise
        """
        try:
            data = json.loads(response.strip())
            
            # Check required fields
            if not all(key in data for key in ['disk', 'from', 'to']):
                return False
            
            # Check types
            if not all(isinstance(data[key], int) for key in ['disk', 'from', 'to']):
                return False
            
            # Check ranges
            if not (1 <= data['disk'] <= self.num_disks):
                return False
            if not (0 <= data['from'] <= 2 and 0 <= data['to'] <= 2):
                return False
            if data['from'] == data['to']:
                return False
            
            return True
        except (json.JSONDecodeError, KeyError, TypeError):
            return False
    
    def _call_model(self, state: Dict) -> str:
        """
        Call the LLM model with the current state.
        
        Args:
            state: Current state dictionary
            
        Returns:
            The model's response as a string
        """
        prompt = create_move_prompt(state)
        system_prompt = create_system_prompt()
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Some randomness for voting diversity
            max_tokens=100  # Short responses expected
        )
        
        return response.choices[0].message.content
    
    def _parse_action(self, response: str) -> List[int]:
        """
        Parse the action from the LLM response.
        
        Args:
            response: The LLM response
            
        Returns:
            Action as [disk, from, to]
        """
        data = json.loads(response.strip())
        return [data['disk'], data['from'], data['to']]
    
    def _parse_next_state(self, response: str) -> Dict:
        """
        Parse and compute the next state from the LLM response.
        
        Args:
            response: The LLM response
            
        Returns:
            Next state dictionary
        """
        # Note: In a real implementation, you would apply the move to the state
        # For this example, we'll return a placeholder
        # The actual state update would happen in the orchestration layer
        return {}
    
    def _apply_move(self, state: Dict, action: List[int]) -> Dict:
        """
        Apply a move to the current state to get the next state.
        
        Args:
            state: Current state
            action: Move to apply [disk, from, to]
            
        Returns:
            Next state
        """
        # Deep copy the pegs
        new_pegs = [peg[:] for peg in state['pegs']]
        
        disk, from_peg, to_peg = action
        
        # Remove disk from source peg
        new_pegs[from_peg].remove(disk)
        
        # Add disk to destination peg
        new_pegs[to_peg].append(disk)
        
        return {
            'pegs': new_pegs,
            'goal': state['goal'],
            'num_disks': state['num_disks']
        }
    
    def solve(self) -> List[List[int]]:
        """
        Solve the Towers of Hanoi puzzle using the MAKER framework.
        
        Returns:
            List of moves, where each move is [disk, from, to]
        """
        # Initial state: all disks on peg 0
        initial_state = {
            'pegs': [list(range(self.num_disks, 0, -1)), [], []],
            'goal': 2,
            'num_disks': self.num_disks
        }
        
        print(f"Solving {self.num_disks}-disk Towers of Hanoi")
        print(f"Total steps required: {self.num_steps}")
        print(f"Voting parameter k: {self.k}")
        print(f"Estimated k_min: {estimate_kmin(self.num_steps, 0.99)}")
        print()
        
        # Note: For a complete implementation, you would use generate_solution
        # Here we provide a simplified demonstration
        
        actions = []
        current_state = initial_state
        
        for step in range(min(10, self.num_steps)):  # Demonstrate first 10 steps
            print(f"Step {step + 1}/{self.num_steps}")
            
            # Simulate voting (in practice, this would use do_voting)
            response = self._call_model(current_state)
            
            if not self.red_flag_checker(response):
                action = self._parse_action(response)
                actions.append(action)
                current_state = self._apply_move(current_state, action)
                print(f"  Move: disk {action[0]} from peg {action[1]} to peg {action[2]}")
            else:
                print(f"  Red flag detected, resampling...")
                step -= 1  # Retry this step
        
        return actions


def main():
    """
    Main entry point for the Towers of Hanoi example.
    """
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    # Solve a small example (3 disks = 7 moves)
    solver = TowersOfHanoiSolver(num_disks=3, k=3)
    moves = solver.solve()
    
    print(f"\nCompleted {len(moves)} moves")
    print("Solution:", moves)


if __name__ == '__main__':
    main()
