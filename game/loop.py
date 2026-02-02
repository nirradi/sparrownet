"""Main game loop skeleton.

Orchestrates: terminal input -> intent -> patch generator (stub or LLM) -> apply_patch -> render

The patch generator can be configured at runtime via mutator_type ("stub" or "llm").
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict
from typing import Optional

from engine import state as state_mod
from engine.patch import apply_patch, PatchResult
from engine.state import Event
from game.commands import parse_intent, IntentType
from game.mutate import get_mutator

LOG = logging.getLogger(__name__)

# Configure root logger from environment so modules like `llm.mutate`
# emitting DEBUG logs are visible when `LOGLEVEL=DEBUG` is set.
_loglevel = os.getenv("LOGLEVEL", "INFO").upper()
try:
	_level = getattr(logging, _loglevel, logging.INFO)
except Exception:
	_level = logging.INFO
logging.basicConfig(level=_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
# Silence overly noisy httpcore/httpx loggers which clutter output
for _n in ("httpcore.http11", "httpcore.connection", "httpx"):
	logging.getLogger(_n).setLevel(logging.WARNING)


def generate_patch_from_intent(intent, state: state_mod.GameState) -> Optional[dict]:
	"""(Deprecated) Generate a deterministic, hard-coded patch stub from an Intent.

	This function is kept for backwards compatibility. Use game.mutate.generate_patch instead.
	"""
	from game.mutate_stub import generate_patch as stub_gen
	patch = stub_gen(intent, state)
	return patch if patch else None


def check_win_condition(state: state_mod.GameState) -> bool:
    """Simple level-1 win condition:

    - clock has been changed from the default (not 00:00), AND
    - at least one email has been sent (player_sent_email event)
    """
    try:
        clock_ok = state.strict.clock.time != "00:00"
    except Exception:
        clock_ok = False

    # Check for at least one player_sent_email event
    email_sent = any(
        e.type == "player_sent_email"
        for e in (state.strict.events or [])
    )
    
    return clock_ok and email_sent


def render_patch_result(result: PatchResult) -> None:
    """Print patch application results: success, errors, warnings."""
    print("Patch apply result:")
    print(f"  success: {result.success}")
    if result.strict_errors:
        print("  strict errors:")
        for err in result.strict_errors:
            print(f"    - {err.field}: {err.reason} (value={err.attempted_value})")
    if result.warnings:
        print("  warnings:")
        for w in result.warnings:
            print(f"    - {w}")


def render_strict_state(state: state_mod.GameState) -> None:
    """Print the strict state for debugging."""
    try:
        strict_dict = asdict(state.strict)
    except Exception:
        # Fallback: serialize via state_to_json and extract 'strict'
        doc = json.loads(state_mod.state_to_json(state))
        strict_dict = doc.get('strict', {})

    print("Current strict state:")
    print(json.dumps(strict_dict, indent=2))


def main(mutator_type: str = "llm") -> None:
	"""Run the main game loop.

	Args:
		mutator_type: "stub" (non-LLM) or "llm" (default, uses LLM mutator).
	"""
	LOG.info("Starting game loop with mutator_type=%s", mutator_type)
	mutator = get_mutator(mutator_type)
	state = state_mod.create_initial_state()

	while True:
		try:
			user_input = input('> ')
		except (EOFError, KeyboardInterrupt):
			print('\nExiting.')
			break

		intent = parse_intent(user_input)
		print(f"Intent: {intent.type.name} (confidence={intent.confidence})")

		# Use the selected mutator to generate the patch
		patch = mutator(intent, state, level_context=None)

		# Handle no-patch intents directly
		if not patch:
			if intent.type is IntentType.SHOW_CONFIG:
				print("System config:")
				print(json.dumps(state.vibe.system_config or {}, indent=2))
			elif intent.type is IntentType.READ_EMAIL:
				print("Inbox:")
				print(json.dumps(state.vibe.emails or [], indent=2))
			else:
				print("No state change proposed.")

			render_strict_state(state)
			if check_win_condition(state):
				print("WIN CONDITION MET — Level complete.")
				break
			continue

		# Apply the proposed patch
		print("Proposed patch:")
		print(json.dumps(patch, indent=2))

		result = apply_patch(state, patch)
		render_patch_result(result)

		if result.success:
			state = result.state

		render_strict_state(state)

		if check_win_condition(state):
			print("WIN CONDITION MET — Level complete.")
			break


if __name__ == '__main__':
    main()
