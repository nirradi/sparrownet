"""Main game loop skeleton.

Orchestrates: terminal input -> intent -> (non-LLM) patch stub -> apply_patch -> render

Designed so the patch generator or renderer can be replaced by an LLM later.
Works without any LLMs for the clock + email level-1 puzzle.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import Optional

from engine import state as state_mod
from engine.patch import apply_patch, PatchResult
from engine.state import Event
from game.commands import parse_intent, IntentType


def generate_patch_from_intent(intent, state: state_mod.GameState) -> Optional[dict]:
    """Generate a deterministic, hard-coded patch stub from an Intent.

    Returns a patch dict suitable for `apply_patch`, or None for no-patch commands.
    """
    itype = intent.type

    # No state mutation for these intents
    if itype in (IntentType.SHOW_CONFIG, IntentType.READ_EMAIL):
        return None

    # SET_CLOCK: expect 'offset_hours' param; update strict.clock.time and append
    # a player_changed_clock event to strict.events to record the change.
    if itype is IntentType.SET_CLOCK:
        offset = intent.params.get('offset_hours')
        if offset is None:
            return None

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
    return None


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


def main() -> None:
    state = state_mod.create_initial_state()

    while True:
        try:
            user_input = input('> ')
        except (EOFError, KeyboardInterrupt):
            print('\nExiting.')
            break

        intent = parse_intent(user_input)
        print(f"Intent: {intent.type.name} (confidence={intent.confidence})")

        patch = generate_patch_from_intent(intent, state)

        # Handle no-patch intents directly
        if patch is None:
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
