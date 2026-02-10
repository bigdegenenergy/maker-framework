"""
MAKER Framework Task Executor

Loads a task configuration (produced by maker_cli.py) and runs it using
the MAKER voting algorithm with micro-agents built from the decomposition.

Usage:
    python -m maker.execute <config_file.json> [--yes] [--output FILE]
    python -m maker.execute --help
"""

import argparse
import json
import re
import sys
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .algorithms import create_red_flag_checker, do_voting
from .decomposer import create_micro_agent_from_decomposition
from .openrouter import OpenRouterClient, format_cost_estimate

REQUIRED_CONFIG_KEYS = [
    "task_description",
    "decomposition",
    "model",
    "k",
    "estimated_steps",
]


def load_and_validate_config(path: str) -> Dict[str, Any]:
    """Load and validate a MAKER task config JSON file.

    Args:
        path: Path to the config JSON file.

    Returns:
        Validated config dictionary.

    Raises:
        FileNotFoundError: If config file does not exist.
        json.JSONDecodeError: If file is not valid JSON.
        ValueError: If required keys are missing.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(config_path, "r") as fh:
        config: Dict[str, Any] = json.load(fh)

    missing = [k for k in REQUIRED_CONFIG_KEYS if k not in config]
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(missing)}")

    decomp = config["decomposition"]
    if "step_types" not in decomp or not decomp["step_types"]:
        raise ValueError(
            "Config decomposition must contain non-empty 'step_types'"
        )

    return config


def build_micro_agents(
    config: Dict[str, Any], client: OpenRouterClient
) -> Dict[str, Callable]:
    """Build a micro-agent callable for each step type in the decomposition.

    Args:
        config: Validated config dictionary.
        client: OpenRouter API client.

    Returns:
        Dict mapping step-type name to its micro-agent callable.
    """
    model = config["model"]
    agents: Dict[str, Callable] = {}
    for step_type in config["decomposition"]["step_types"]:
        name = step_type["name"]
        agents[name] = create_micro_agent_from_decomposition(
            step_type, client, model
        )
    return agents


def build_red_flag_checker(step_type: Dict[str, Any]) -> Callable[[str], bool]:
    """Build a red-flag checker for a step type.

    Combines the generic format-length checker from ``create_red_flag_checker``
    with custom indicator-string matching from the decomposition config.

    Args:
        step_type: A single step-type dict from the decomposition.

    Returns:
        Callable that returns True when red flags are detected.
    """
    indicators: List[str] = step_type.get("red_flag_indicators", [])
    lower_indicators = [ind.lower() for ind in indicators]

    base_checker = create_red_flag_checker(max_tokens=750)

    def checker(response: str) -> bool:
        if base_checker(response):
            return True
        resp_lower = response.lower()
        return any(ind in resp_lower for ind in lower_indicators)

    return checker


def create_step_type_selector(
    config: Dict[str, Any], client: Optional[OpenRouterClient] = None
) -> Callable[[Dict[str, Any], int], str]:
    """Create a function that selects the step-type name for each step.

    For single step-type tasks, returns a constant selector.
    For multi step-type tasks, uses an LLM call to choose.

    Args:
        config: Validated config dictionary.
        client: OpenRouter client (required for multi step-type tasks).

    Returns:
        Callable(state, step_number) -> step_type_name.
    """
    step_types = config["decomposition"]["step_types"]

    if len(step_types) == 1:
        name = step_types[0]["name"]
        return lambda _state, _step: name

    names = [st["name"] for st in step_types]
    descriptions = {st["name"]: st["description"] for st in step_types}

    def selector(state: Dict[str, Any], step: int) -> str:
        if client is None:
            return names[step % len(names)]

        options = "\n".join(
            f"- {n}: {descriptions[n]}" for n in names
        )
        prompt = (
            f"Task: {state.get('task_description', '')}\n"
            f"Current step: {step + 1}\n"
            f"Previous actions: {len(state.get('action_history', []))}\n\n"
            f"Available step types:\n{options}\n\n"
            f"Which step type should be used for this step? "
            f"Reply with ONLY the step type name."
        )
        messages = [
            {"role": "system", "content": "You select the correct step type. Reply with only the name."},
            {"role": "user", "content": prompt},
        ]
        response = client.chat_completion(
            model=config["model"],
            messages=messages,
            temperature=0.0,
            max_tokens=50,
        )
        chosen = response.strip()
        return chosen if chosen in names else names[0]

    return selector


def parse_action_from_response(response: str) -> Any:
    """Extract a structured action from an LLM response.

    Tries to parse JSON (optionally wrapped in markdown code fences).
    Falls back to returning the raw text.

    Args:
        response: Raw LLM response string.

    Returns:
        Parsed JSON object, or the raw string if JSON parsing fails.
    """
    if not response:
        return response

    text = response.strip()

    # Try markdown-wrapped JSON
    md_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if md_match:
        try:
            return json.loads(md_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try plain JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON object from surrounding text
    json_match = re.search(r"\{[^{}]*\}", text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return response


def create_state_updater(
    config: Dict[str, Any],
) -> Callable[[Dict[str, Any], Any, int], Dict[str, Any]]:
    """Create a function that updates the task state after each step.

    The updater accumulates action history and increments the step counter
    without mutating the original state dict.

    Args:
        config: Validated config dictionary.

    Returns:
        Callable(state, action, step_number) -> new_state.
    """

    def updater(
        state: Dict[str, Any], action: Any, step_number: int
    ) -> Dict[str, Any]:
        new_state = deepcopy(state)
        new_state["current_step"] = step_number
        new_state.setdefault("action_history", []).append(action)
        return new_state

    return updater


def execute_task(
    config: Dict[str, Any],
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute a MAKER task from a validated config.

    Args:
        config: Validated config dictionary.
        api_key: OpenRouter API key (falls back to env var).

    Returns:
        Result dict with keys: completed, steps_completed, actions, final_state.
    """
    client = OpenRouterClient(api_key=api_key)

    num_steps = config["estimated_steps"]
    k = config["k"]

    micro_agents = build_micro_agents(config, client)
    selector = create_step_type_selector(config, client)
    state_updater = create_state_updater(config)

    checkers: Dict[str, Callable] = {}
    for step_type in config["decomposition"]["step_types"]:
        checkers[step_type["name"]] = build_red_flag_checker(step_type)

    current_state: Dict[str, Any] = {
        "task_description": config["task_description"],
        "success_criteria": config.get("success_criteria", ""),
        "current_step": 0,
        "total_steps": num_steps,
        "action_history": [],
    }

    actions: List[Any] = []

    def _make_parse_next_state(
        st: Dict[str, Any],
    ) -> Callable[[str], Dict[str, Any]]:
        """Return a parse_next_state that just returns the current state."""
        return lambda _response: st

    try:
        for step in range(num_steps):
            step_type_name = selector(current_state, step)
            model_fn = micro_agents[step_type_name]
            check_fn = checkers[step_type_name]

            action, _ = do_voting(
                current_state,
                model_fn,
                k,
                parse_action_from_response,
                _make_parse_next_state(current_state),
                check_fn,
            )

            actions.append(action)
            current_state = state_updater(current_state, action, step + 1)

            _print_step_progress(step + 1, num_steps, step_type_name, action)

    except KeyboardInterrupt:
        print(f"\n\nInterrupted at step {len(actions)}/{num_steps}.")
        return {
            "completed": False,
            "steps_completed": len(actions),
            "actions": actions,
            "final_state": current_state,
        }

    return {
        "completed": True,
        "steps_completed": num_steps,
        "actions": actions,
        "final_state": current_state,
    }


def _print_step_progress(
    step: int, total: int, step_type: str, action: Any
) -> None:
    """Print a single line of step progress."""
    action_preview = str(action)[:60]
    print(f"  [{step}/{total}] ({step_type}) {action_preview}")


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point for ``python -m maker.execute``.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 success, 1 error).
    """
    parser = argparse.ArgumentParser(
        prog="python -m maker.execute",
        description="Execute a MAKER task from a configuration file.",
    )
    parser.add_argument(
        "config",
        help="Path to the task configuration JSON file",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompt",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Path to save results JSON (default: <config>_results.json)",
    )
    args = parser.parse_args(argv)

    try:
        config = load_and_validate_config(args.config)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 1

    print(f"\nTask: {config['task_description']}")
    print(f"Steps: {config['estimated_steps']}")
    print(f"Model: {config['model']}")
    print(f"Voting k: {config['k']}")

    cost_est = config.get("cost_estimate")
    if cost_est:
        print(f"Estimated cost: ${cost_est.get('total_cost', 0):.4f}")

    if not args.yes:
        confirm = input("\nProceed with execution? (y/n): ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return 0

    print(f"\nExecuting task ({config['estimated_steps']} steps)...\n")
    start = time.time()

    try:
        result = execute_task(config)
    except ValueError as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        return 1

    elapsed = time.time() - start
    print(f"\nCompleted: {result['steps_completed']}/{config['estimated_steps']} steps")
    print(f"Time: {elapsed:.1f}s")

    output_path = args.output or args.config.replace(".json", "_results.json")
    result_serializable = {
        "completed": result["completed"],
        "steps_completed": result["steps_completed"],
        "actions": result["actions"],
        "elapsed_seconds": round(elapsed, 2),
        "config_file": args.config,
    }
    with open(output_path, "w") as fh:
        json.dump(result_serializable, fh, indent=2, default=str)
    print(f"Results saved to: {output_path}")

    return 0 if result["completed"] else 1


if __name__ == "__main__":
    sys.exit(main())
