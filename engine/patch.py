"""Patch schema and utilities.

This module applies LLM-generated patches to the game state.

Patches describe desired state changes in two categories:
  - strict: Changes to authoritative game state that must be validated
  - vibe: Ambient narrative state that can be flexible

Key design principles:
  - Deterministic and testable
  - Patches are declarative (desired state), not imperative (instructions)
  - Validation is strict for game-critical state, permissive for narrative
  - No external side effects (no filesystem, network, clock calls)
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from copy import deepcopy

from engine.state import GameState, StrictState, VibeState, Clock, Event


# Type alias for a patch dictionary
Patch = dict[str, Any]


@dataclass
class ValidationError:
    """A single validation error in strict state."""
    field: str
    reason: str
    attempted_value: Any


@dataclass
class PatchResult:
    """Result of applying a patch to game state.
    
    Attributes:
        success: Whether the patch was fully applied.
        state: The resulting game state (original if failed, modified otherwise).
        strict_errors: Validation errors encountered in strict patches.
        warnings: Non-fatal issues encountered.
    """
    success: bool
    state: GameState
    strict_errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _validate_clock(value: Any) -> tuple[bool, Optional[str]]:
    """Validate a clock object.
    
    Args:
        value: Potential clock patch (dict-like).
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not isinstance(value, dict):
        return False, "Clock must be a dict"
    
    # Both timezone and time must be present if clock is being patched
    if "timezone" in value and not isinstance(value["timezone"], str):
        return False, "timezone must be a string"
    
    if "time" in value:
        time_val = value["time"]
        if not isinstance(time_val, str):
            return False, "time must be a string"
        # Basic HH:MM format check
        if len(time_val) != 5 or time_val[2] != ":":
            return False, "time must be in HH:MM format"
        try:
            hour, minute = time_val.split(":")
            h = int(hour)
            m = int(minute)
            if not (0 <= h <= 23) or not (0 <= m <= 59):
                return False, "time out of bounds (HH must be 00-23, MM must be 00-59)"
        except ValueError:
            return False, "time components must be numeric"
    
    return True, None


def _validate_email_sent(value: Any) -> tuple[bool, Optional[str]]:
    """Validate an email sent event object.
    
    Args:
        value: Potential event patch (dict-like).
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not isinstance(value, dict):
        return False, "Event must be a dict"
    
    # Must have recipient and sent_at
    if "recipient" not in value:
        return False, "recipient is required"
    
    recipient = value["recipient"]
    if not isinstance(recipient, str):
        return False, "recipient must be a string"
    
    # Basic email validation
    if "@" not in recipient or "." not in recipient.split("@")[-1]:
        return False, "recipient must be a valid email address"
    
    if "sent_at" not in value:
        return False, "sent_at is required"
    
    sent_at = value["sent_at"]
    if not isinstance(sent_at, str):
        return False, "sent_at must be a string"
    
    # Basic HH:MM format check
    if len(sent_at) != 5 or sent_at[2] != ":":
        return False, "sent_at must be in HH:MM format"
    
    try:
        hour, minute = sent_at.split(":")
        h = int(hour)
        m = int(minute)
        if not (0 <= h <= 23) or not (0 <= m <= 59):
            return False, "sent_at out of bounds"
    except ValueError:
        return False, "sent_at components must be numeric"
    
    return True, None


def _validate_clock_change(value: Any) -> tuple[bool, Optional[str]]:
    """Validate a clock change event object.
    
    Args:
        value: Potential event patch (dict-like).
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not isinstance(value, dict):
        return False, "Event must be a dict"
    
    if "changed_at" not in value:
        return False, "changed_at is required"
    
    changed_at = value["changed_at"]
    if not isinstance(changed_at, str):
        return False, "changed_at must be a string"
    
    # Basic HH:MM format check
    if len(changed_at) != 5 or changed_at[2] != ":":
        return False, "changed_at must be in HH:MM format"
    
    try:
        hour, minute = changed_at.split(":")
        h = int(hour)
        m = int(minute)
        if not (0 <= h <= 23) or not (0 <= m <= 59):
            return False, "changed_at out of bounds"
    except ValueError:
        return False, "changed_at components must be numeric"
    
    return True, None


def _apply_strict_patch(
    current_strict: StrictState,
    patch_dict: dict[str, Any]
) -> tuple[StrictState, list[ValidationError]]:
    """Apply and validate a strict patch.
    
    This function preserves the original state and only modifies what is
    explicitly provided in the patch, after validation passes.
    
    Args:
        current_strict: Current strict state.
        patch_dict: Patch data for strict state.
        
    Returns:
        Tuple of (updated_strict_state, validation_errors).
        If any field fails validation, that field is not applied.
        Returns original state with errors if validation fails.
    """
    errors: list[ValidationError] = []
    
    # Create a working copy
    updated = deepcopy(current_strict)
    
    # Validate and apply clock patch
    if "clock" in patch_dict:
        clock_patch = patch_dict["clock"]
        is_valid, error_msg = _validate_clock(clock_patch)
        
        if not is_valid:
            errors.append(
                ValidationError(
                    field="clock",
                    reason=error_msg,
                    attempted_value=clock_patch
                )
            )
        else:
            # Apply valid clock patch
            current_tz = updated.clock.timezone
            current_time = updated.clock.time
            
            new_tz = clock_patch.get("timezone", current_tz)
            new_time = clock_patch.get("time", current_time)
            
            updated.clock = Clock(timezone=new_tz, time=new_time)
    
    # Validate and apply events patch
    if "events" in patch_dict:
        events_patch = patch_dict["events"]
        
        if not isinstance(events_patch, list):
            errors.append(
                ValidationError(
                    field="events",
                    reason="events must be a list",
                    attempted_value=events_patch
                )
            )
        else:
            # Validate each event in the list
            valid_events = []
            for idx, event in enumerate(events_patch):
                if not isinstance(event, dict):
                    errors.append(
                        ValidationError(
                            field=f"events[{idx}]",
                            reason="event must be a dict",
                            attempted_value=event
                        )
                    )
                    continue
                
                # Check event type
                event_type = event.get("type")
                if event_type not in ("player_changed_clock", "player_sent_email"):
                    errors.append(
                        ValidationError(
                            field=f"events[{idx}]",
                            reason="type must be 'player_changed_clock' or 'player_sent_email'",
                            attempted_value=event
                        )
                    )
                    continue
                
                # Validate based on type
                if event_type == "player_changed_clock":
                    is_valid, error_msg = _validate_clock_change(event)
                    if not is_valid:
                        errors.append(
                            ValidationError(
                                field=f"events[{idx}]",
                                reason=error_msg,
                                attempted_value=event
                            )
                        )
                    else:
                        event_obj = Event(type="player_changed_clock", changed_at=event["changed_at"])
                        valid_events.append(event_obj)
                
                elif event_type == "player_sent_email":
                    is_valid, error_msg = _validate_email_sent(event)
                    if not is_valid:
                        errors.append(
                            ValidationError(
                                field=f"events[{idx}]",
                                reason=error_msg,
                                attempted_value=event
                            )
                        )
                    else:
                        event_obj = Event(type="player_sent_email", recipient=event["recipient"], sent_at=event["sent_at"])
                        valid_events.append(event_obj)
            
            # Only update events if no errors were found
            if not errors:
                updated.events = valid_events
    
    return updated, errors


def _apply_vibe_patch(
    current_vibe: VibeState,
    patch_dict: dict[str, Any]
) -> tuple[VibeState, list[str]]:
    """Apply a vibe patch permissively.
    
    Vibe patches have minimal validation - just structural sanity checks.
    Missing or mistyped fields are tolerated to keep narrative flexible.
    
    Args:
        current_vibe: Current vibe state.
        patch_dict: Patch data for vibe state.
        
    Returns:
        Tuple of (updated_vibe_state, warnings).
    """
    warnings: list[str] = []
    
    # Create a working copy
    updated = deepcopy(current_vibe)
    
    # Apply system_config patch
    if "system_config" in patch_dict:
        config_patch = patch_dict["system_config"]
        if isinstance(config_patch, dict):
            updated.system_config = config_patch
        else:
            warnings.append(f"system_config should be a dict, got {type(config_patch).__name__}")
    
    # Apply emails patch
    if "emails" in patch_dict:
        emails_patch = patch_dict["emails"]
        if isinstance(emails_patch, list):
            updated.emails = emails_patch
        else:
            warnings.append(f"emails should be a list, got {type(emails_patch).__name__}")
    
    # Apply notes patch
    if "notes" in patch_dict:
        notes_patch = patch_dict["notes"]
        if isinstance(notes_patch, list):
            updated.notes = notes_patch
        else:
            warnings.append(f"notes should be a list, got {type(notes_patch).__name__}")
    
    return updated, warnings


def apply_patch(state: GameState, patch: Patch) -> PatchResult:
    """Apply a patch to the game state.
    
    Patches have two top-level keys:
      - strict: Validated, game-critical state changes
      - vibe: Flexible, narrative-only state changes
    
    Strict patches are validated before application. If validation fails,
    those fields are not applied. Vibe patches are applied permissively.
    
    Args:
        state: Current game state.
        patch: Patch dict with "strict" and/or "vibe" keys.
        
    Returns:
        PatchResult: Contains updated state, errors, and warnings.
        
    Example:
        patch = {
            "strict": {
                "clock": {"time": "09:00"},
                "events": [{"recipient": "admin@example.com", "sent_at": "08:30"}]
            },
            "vibe": {
                "notes": ["User felt clever"]
            }
        }
        result = apply_patch(state, patch)
        if result.success:
            state = result.state
    """
    # Start with a copy of the current state
    updated_state = deepcopy(state)
    all_errors: list[ValidationError] = []
    all_warnings: list[str] = []
    
    # Apply strict patches with validation
    if "strict" in patch:
        strict_patch = patch["strict"]
        if isinstance(strict_patch, dict):
            updated_strict, strict_errors = _apply_strict_patch(
                updated_state.strict,
                strict_patch
            )
            all_errors.extend(strict_errors)
            updated_state.strict = updated_strict
        else:
            all_warnings.append("strict patch should be a dict, skipping")
    
    # Apply vibe patches permissively
    if "vibe" in patch:
        vibe_patch = patch["vibe"]
        if isinstance(vibe_patch, dict):
            updated_vibe, vibe_warnings = _apply_vibe_patch(
                updated_state.vibe,
                vibe_patch
            )
            all_warnings.extend(vibe_warnings)
            updated_state.vibe = updated_vibe
        else:
            all_warnings.append("vibe patch should be a dict, skipping")
    
    # Success if no strict validation errors occurred
    success = len(all_errors) == 0
    
    return PatchResult(
        success=success,
        state=updated_state,
        strict_errors=all_errors,
        warnings=all_warnings
    )
