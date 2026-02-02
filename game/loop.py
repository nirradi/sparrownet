

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
from dataclasses import dataclass

from game.narrate import narrate


@dataclass
class Outcome:
	intent_type: str
	intent_confidence: float
	patch: dict | None
	success: bool
	errors: list[str]


from game.commands import parse_intent
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
        e.recipient == "ops@corp" and e.sent_at != "00:00"
        for e in (state.strict.emails or [])
    )
    
    return clock_ok and email_sent


def render_patch_result(result: PatchResult) -> None:
	"""Print patch application results: success, errors, warnings."""
	LOG.debug("Patch apply result:")
	LOG.debug(f"  success: {result.success}")
	if result.strict_errors:
		LOG.debug("  strict errors:")
		for err in result.strict_errors:
			LOG.debug(f"    - {err.field}: {err.reason} (value={err.attempted_value})")
	if result.warnings:
		LOG.debug("  warnings:")
		for w in result.warnings:
			LOG.debug(f"    - {w}")


def render_strict_state(state: state_mod.GameState) -> None:
    """Print the strict state for debugging."""
    try:
        strict_dict = asdict(state.strict)
    except Exception:
        # Fallback: serialize via state_to_json and extract 'strict'
        doc = json.loads(state_mod.state_to_json(state))
        strict_dict = doc.get('strict', {})
    LOG.debug("Current strict state:")
    LOG.debug(json.dumps(strict_dict, indent=2))


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
			LOG.debug('Exiting.')
			break

		intent = parse_intent(user_input)
		LOG.debug(f"Intent: {intent.type.name} (confidence={intent.confidence})")

		# Use the selected mutator to generate the patch
		patch = mutator(intent, state, level_context=None)

		result = None
		if patch:
			LOG.debug("Proposed patch:")
			LOG.debug(json.dumps(patch, indent=2))
			result = apply_patch(state, patch)
			render_patch_result(result)
			if result and result.success:
				state = result.state

		outcome = Outcome(
			intent_type=intent.type.name,
			intent_confidence=float(intent.confidence),
			patch=patch if patch else None,
			success=bool(result.success) if result else False,
			errors=[f"{e.field}: {e.reason} (value={e.attempted_value})" for e in (result.strict_errors if result and result.strict_errors else [])]
		)
		narration = narrate(outcome)
		print(narration.text)

		render_strict_state(state)

		if check_win_condition(state):
			print("WIN CONDITION MET — Level complete.")
			break


if __name__ == '__main__':
    main()
