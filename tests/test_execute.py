"""Tests for maker.execute module."""

import json
import os
import sys
import tempfile
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from maker.execute import (
    create_state_updater,
    execute_task,
    load_and_validate_config,
    parse_action_from_response,
)


# --- Fixtures ---


def _make_config(overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Build a minimal valid config dict."""
    config: Dict[str, Any] = {
        "task_description": "Test task",
        "success_criteria": "Done",
        "model": "google/gemini-2.0-flash-001",
        "k": 2,
        "estimated_steps": 3,
        "decomposition": {
            "estimated_steps": 3,
            "step_types": [
                {
                    "name": "solve",
                    "description": "Solve a step",
                    "frequency": "every step",
                    "micro_agent_prompt": "Do step for {current_step}",
                    "output_format": "JSON",
                    "red_flag_indicators": ["ERROR", "I don't know"],
                }
            ],
            "execution_order": "sequential",
            "state_representation": "action history",
        },
        "cost_estimate": {"total_cost": 0.001},
    }
    if overrides:
        config.update(overrides)
    return config


@pytest.fixture()
def valid_config() -> Dict[str, Any]:
    return _make_config()


@pytest.fixture()
def config_file(valid_config: Dict[str, Any]) -> str:
    """Write a valid config to a temp file and return its path."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as fh:
        json.dump(valid_config, fh)
        return fh.name


# --- load_and_validate_config ---


class TestLoadAndValidateConfig:
    def test_valid_config(self, config_file: str) -> None:
        cfg = load_and_validate_config(config_file)
        assert cfg["task_description"] == "Test task"
        assert cfg["k"] == 2

    def test_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_and_validate_config("/nonexistent/path.json")

    def test_invalid_json(self, tmp_path: Any) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text("not json{{{")
        with pytest.raises(json.JSONDecodeError):
            load_and_validate_config(str(bad))

    def test_missing_required_key(self, tmp_path: Any) -> None:
        incomplete = tmp_path / "incomplete.json"
        incomplete.write_text(json.dumps({"task_description": "only this"}))
        with pytest.raises(ValueError, match="Missing required"):
            load_and_validate_config(str(incomplete))

    def test_missing_decomposition_step_types(self, tmp_path: Any) -> None:
        cfg = _make_config()
        cfg["decomposition"] = {"estimated_steps": 3}
        bad = tmp_path / "no_steps.json"
        bad.write_text(json.dumps(cfg))
        with pytest.raises(ValueError, match="step_types"):
            load_and_validate_config(str(bad))


# --- parse_action_from_response ---


class TestParseActionFromResponse:
    def test_plain_json(self) -> None:
        resp = '{"action": "move", "target": "A"}'
        result = parse_action_from_response(resp)
        assert result == {"action": "move", "target": "A"}

    def test_markdown_wrapped_json(self) -> None:
        resp = '```json\n{"action": "move"}\n```'
        result = parse_action_from_response(resp)
        assert result == {"action": "move"}

    def test_markdown_no_lang_tag(self) -> None:
        resp = '```\n{"action": "move"}\n```'
        result = parse_action_from_response(resp)
        assert result == {"action": "move"}

    def test_plain_text_fallback(self) -> None:
        resp = "Move disk 1 from peg A to peg C"
        result = parse_action_from_response(resp)
        assert result == resp

    def test_json_with_surrounding_text(self) -> None:
        resp = 'Here is the answer:\n{"action": "move"}\nDone.'
        result = parse_action_from_response(resp)
        assert result == {"action": "move"}

    def test_empty_string(self) -> None:
        result = parse_action_from_response("")
        assert result == ""


# --- create_state_updater ---


class TestCreateStateUpdater:
    def test_accumulates_actions(self, valid_config: Dict[str, Any]) -> None:
        updater = create_state_updater(valid_config)
        state: Dict[str, Any] = {
            "task_description": "Test",
            "current_step": 0,
            "action_history": [],
        }
        new_state = updater(state, {"action": "first"}, 1)
        assert new_state["current_step"] == 1
        assert len(new_state["action_history"]) == 1
        assert new_state["action_history"][0] == {"action": "first"}

    def test_increments_step(self, valid_config: Dict[str, Any]) -> None:
        updater = create_state_updater(valid_config)
        state: Dict[str, Any] = {
            "task_description": "Test",
            "current_step": 0,
            "action_history": [],
        }
        s1 = updater(state, "a", 1)
        s2 = updater(s1, "b", 2)
        assert s2["current_step"] == 2
        assert len(s2["action_history"]) == 2

    def test_does_not_mutate_original(self, valid_config: Dict[str, Any]) -> None:
        updater = create_state_updater(valid_config)
        state: Dict[str, Any] = {
            "task_description": "Test",
            "current_step": 0,
            "action_history": [],
        }
        updater(state, "a", 1)
        assert state["current_step"] == 0
        assert len(state["action_history"]) == 0


# --- Red flag checker via build_red_flag_checker ---


class TestBuildRedFlagChecker:
    def test_no_red_flags(self) -> None:
        from maker.execute import build_red_flag_checker

        step_type = {
            "red_flag_indicators": ["ERROR", "I don't know"],
            "output_format": "JSON",
        }
        checker = build_red_flag_checker(step_type)
        assert checker('{"action": "move"}') is False

    def test_indicator_detected(self) -> None:
        from maker.execute import build_red_flag_checker

        step_type = {
            "red_flag_indicators": ["ERROR", "I don't know"],
            "output_format": "JSON",
        }
        checker = build_red_flag_checker(step_type)
        assert checker("ERROR: something went wrong") is True

    def test_case_insensitive_indicator(self) -> None:
        from maker.execute import build_red_flag_checker

        step_type = {
            "red_flag_indicators": ["I don't know"],
            "output_format": "JSON",
        }
        checker = build_red_flag_checker(step_type)
        assert checker("i don't know how to proceed") is True

    def test_no_indicators_configured(self) -> None:
        from maker.execute import build_red_flag_checker

        step_type = {"red_flag_indicators": [], "output_format": "text"}
        checker = build_red_flag_checker(step_type)
        assert checker("anything goes") is False


# --- execute_task (end-to-end with mocks) ---


class TestExecuteTask:
    @patch("maker.execute.OpenRouterClient")
    def test_runs_all_steps(self, mock_client_cls: MagicMock) -> None:
        """Execute a 3-step task with a mocked LLM that returns consistent JSON."""
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = '{"action": "step_done"}'
        mock_client_cls.return_value = mock_client

        config = _make_config({"estimated_steps": 3, "k": 1})
        config["decomposition"]["estimated_steps"] = 3

        result = execute_task(config, api_key="fake-key")

        assert result["completed"] is True
        assert result["steps_completed"] == 3
        assert len(result["actions"]) == 3

    @patch("maker.execute.OpenRouterClient")
    def test_handles_plain_text_response(
        self, mock_client_cls: MagicMock
    ) -> None:
        mock_client = MagicMock()
        mock_client.chat_completion.return_value = "Move disk 1 to peg C"
        mock_client_cls.return_value = mock_client

        config = _make_config({"estimated_steps": 2, "k": 1})
        config["decomposition"]["estimated_steps"] = 2
        # Remove red flag indicators so plain text isn't flagged
        config["decomposition"]["step_types"][0]["red_flag_indicators"] = []

        result = execute_task(config, api_key="fake-key")

        assert result["completed"] is True
        assert result["steps_completed"] == 2

    @patch("maker.execute.OpenRouterClient")
    def test_returns_partial_on_keyboard_interrupt(
        self, mock_client_cls: MagicMock
    ) -> None:
        mock_client = MagicMock()
        call_count = 0

        def side_effect(*args: Any, **kwargs: Any) -> str:
            nonlocal call_count
            call_count += 1
            if call_count > 2:
                raise KeyboardInterrupt()
            return '{"action": "ok"}'

        mock_client.chat_completion.side_effect = side_effect
        mock_client_cls.return_value = mock_client

        config = _make_config({"estimated_steps": 5, "k": 1})
        config["decomposition"]["estimated_steps"] = 5

        result = execute_task(config, api_key="fake-key")

        assert result["completed"] is False
        assert result["steps_completed"] < 5
        assert len(result["actions"]) > 0


# --- Cleanup temp files ---


@pytest.fixture(autouse=True)
def _cleanup_config_files(config_file: str) -> Any:
    yield
    if os.path.exists(config_file):
        os.unlink(config_file)
