"""State model and helpers."""
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, Union
from copy import deepcopy

from dataclasses_jsonschema import JsonSchemaMixin



@dataclass
class Clock(JsonSchemaMixin):
    """Clock state: timezone and current time."""
    timezone: str
    time: str  # HH:MM format


@dataclass
class Email(JsonSchemaMixin):
    """Email with recipient field."""
    recipient: str
    sent_at: Optional[str] = None  # Optional sent_at time in HH:MM


@dataclass
class StrictState(JsonSchemaMixin):
    """
    Closed-schema state used for win conditions and validation.
    
    No dynamic keys allowed. Structure is fixed and enforced.
    """
    clock: Clock
    emails: list[Email] = field(default_factory=list)


@dataclass
class VibeState:
    """
    Free-form, realism-only state.
    
    Not used for win conditions or validation.
    Can be extended with narrative details.
    """
    system_config: dict = field(default_factory=dict)
    emails: list = field(default_factory=list)
    notes: list = field(default_factory=list)


@dataclass
class GameState:
    """Top-level game state with strict and vibe components."""
    strict: StrictState
    vibe: VibeState


def create_initial_state() -> GameState:
    """
    Create an initial game state with default values.
    
    Returns:
        GameState: Fresh game state ready for play.
    """
    return GameState(
        strict=StrictState(
            clock=Clock(timezone="UTC", time="00:00"),
            emails=[]
        ),
        vibe=VibeState(
            system_config={},
            emails=[],
        )
    )


def copy_state(state: GameState) -> GameState:
    """
    Deep-copy a game state safely.
    
    Args:
        state: GameState to copy.
        
    Returns:
        GameState: Independent copy with no shared references.
    """
    return deepcopy(state)


def state_to_json(state: GameState) -> str:
    """
    Serialize game state to JSON string.
    
    Args:
        state: GameState to serialize.
        
    Returns:
        str: JSON representation of the state.
    """
    return json.dumps(asdict(state), indent=2)


def state_from_json(json_str: str) -> GameState:
    """
    Deserialize game state from JSON string.
    
    Args:
        json_str: JSON string containing serialized state.
        
    Returns:
        GameState: Reconstructed state object.
        
    Raises:
        json.JSONDecodeError: If JSON is invalid.
        KeyError: If required fields are missing.
        TypeError: If field types don't match.
    """
    data = json.loads(json_str)
    
    strict = StrictState(
        clock=Clock(
            timezone=data["strict"]["clock"]["timezone"],
            time=data["strict"]["clock"]["time"]
        ),
        emails=[Email(**email) for email in data["strict"].get("emails", [])]
    )
    
    vibe = VibeState(
        system_config=data["vibe"]["system_config"],
        emails=data["vibe"]["emails"],
        notes=data["vibe"]["notes"]
    )
    
    return GameState(strict=strict, vibe=vibe)


def strict_state_schema() -> dict:
    """
    Return a JSON schema for StrictState.
    Useful for LLM prompt context and validation.
    """
    return StrictState.json_schema()