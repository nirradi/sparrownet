"""Stub (non-LLM) patch generator for the game loop.

This is a deterministic, hard-coded patch generator for testing and
quick iteration without requiring an LLM.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from engine.state import GameState
from game.commands import IntentType


def generate_patch(intent: Any, state: GameState, level_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
	"""Generate a deterministic, hard-coded patch stub from an Intent.

	Args:
		intent: The parsed Intent object.
		state: The current GameState.
		level_context: Optional context dict (unused in stub).

	Returns:
		A patch dict suitable for `engine.patch.apply_patch`, or {} for no-patch intents.
	"""
	itype = intent.type

	# No state mutation for these intents
	if itype in (IntentType.SHOW_CONFIG, IntentType.READ_EMAIL):
		return {}

	# SET_CLOCK: expect 'offset_hours' param; update strict.clock.time and append
	# a player_changed_clock event to strict.events to record the change.
	if itype is IntentType.SET_CLOCK:
		offset = intent.params.get('offset_hours')
		if offset is None:
			return {}

		# Compute new time by offsetting current strict clock time (HH:MM)
		cur = state.strict.clock.time
		try:
			hh, mm = map(int, cur.split(':'))
		except Exception:
			hh, mm = 0, 0

		new_h = (hh + int(offset)) % 24
		new_time = f"{new_h:02d}:{mm:02d}"

		# Build events patch by preserving existing events and appending
		existing_events = []
		for e in state.strict.events:
			if e.type == "player_changed_clock":
				existing_events.append({'type': 'player_changed_clock', 'changed_at': e.changed_at})
			elif e.type == "player_sent_email":
				existing_events.append({'type': 'player_sent_email', 'recipient': e.recipient, 'sent_at': e.sent_at})

		clock_event = {'type': 'player_changed_clock', 'changed_at': new_time}
		events_patch = existing_events + [clock_event]

		return {'strict': {'clock': {'time': new_time}, 'events': events_patch}}

	# SEND_EMAIL: update vibe.emails (append) and record a strict player_sent_email event
	if itype is IntentType.SEND_EMAIL:
		recipient = intent.params.get('recipient', '')
		body = intent.params.get('body', '')

		sent_at = state.strict.clock.time

		# Vibe emails: append a simple dict
		existing_vibe = list(state.vibe.emails or [])
		new_vibe_email = {'recipient': recipient, 'body': body, 'sent_at': sent_at}
		vibe_patch = {'emails': existing_vibe + [new_vibe_email]}

		# Strict events: append a player_sent_email event
		existing_events = []
		for e in state.strict.events:
			if e.type == "player_changed_clock":
				existing_events.append({'type': 'player_changed_clock', 'changed_at': e.changed_at})
			elif e.type == "player_sent_email":
				existing_events.append({'type': 'player_sent_email', 'recipient': e.recipient, 'sent_at': e.sent_at})

		email_event = {'type': 'player_sent_email', 'recipient': recipient, 'sent_at': sent_at}
		events_patch = existing_events + [email_event]

		return {'vibe': vibe_patch, 'strict': {'events': events_patch}}

	# Unknown or unhandled intents produce no patch
	return {}
