"""
MAKER Framework - Core Implementation

Maximal Agentic decomposition, first-to-ahead-by-K Error correction, and Red-flagging

Based on the paper "Solving a Million-Step LLM Task with Zero Errors"
arXiv:2511.09030
"""

from .algorithms import (
    generate_solution,
    do_voting,
    get_vote,
    create_red_flag_checker,
    estimate_kmin
)

__all__ = [
    'generate_solution',
    'do_voting',
    'get_vote',
    'create_red_flag_checker',
    'estimate_kmin'
]

__version__ = '0.1.0'
