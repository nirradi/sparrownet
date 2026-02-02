"""Mutator factory for selecting between stub and LLM patch generators."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from engine.state import GameState

LOG = logging.getLogger(__name__)


def get_mutator(mutator_type: str = "llm"):
	"""Return the appropriate patch generator function based on type.

	Args:
		mutator_type: "stub" or "llm" (default).

	Returns:
		A callable with signature: generate_patch(intent, state, level_context) -> dict

	Raises:
		ValueError: If mutator_type is unknown.
	"""
	if mutator_type == "stub":
		from game.mutate_stub import generate_patch as stub_gen
		LOG.info("Using stub (non-LLM) mutator")
		return stub_gen
	elif mutator_type == "llm":
		from llm.mutate import generate_patch as llm_gen
		LOG.info("Using LLM mutator")
		return llm_gen
	else:
		raise ValueError(f"Unknown mutator_type: {mutator_type}")


def generate_patch(intent: Any, state: GameState, level_context: Optional[Dict[str, Any]] = None, mutator_type: str = "llm") -> Dict[str, Any]:
	"""Convenience wrapper: select and call the appropriate mutator.

	Args:
		intent: The parsed Intent object.
		state: The current GameState.
		level_context: Optional context dict.
		mutator_type: "stub" or "llm".

	Returns:
		A patch dict.
	"""
	mutator = get_mutator(mutator_type)
	try:
		return mutator(intent, state, level_context)
	except Exception as exc:
		LOG.error("Mutator (%s) failed: %s", mutator_type, exc, exc_info=True)
		return {}
