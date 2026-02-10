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

from .openrouter import (
    OpenRouterClient,
    estimate_cost,
    format_cost_estimate,
    get_recommended_model,
    list_available_models
)

from .decomposer import (
    TaskDecomposer,
    create_micro_agent_from_decomposition
)


def __getattr__(name: str):
    """Lazy import for execute_task to avoid conflict with python -m maker.execute."""
    if name == "execute_task":
        from .execute import execute_task
        return execute_task
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Algorithms
    'generate_solution',
    'do_voting',
    'get_vote',
    'create_red_flag_checker',
    'estimate_kmin',
    # OpenRouter
    'OpenRouterClient',
    'estimate_cost',
    'format_cost_estimate',
    'get_recommended_model',
    'list_available_models',
    # Decomposer
    'TaskDecomposer',
    'create_micro_agent_from_decomposition',
    # Executor
    'execute_task',
]

__version__ = '0.2.0'
