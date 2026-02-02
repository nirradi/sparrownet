"""State model and helpers."""
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, Union
from copy import deepcopy


@dataclass
class Clock:
    """Clock state: timezone and current time."""
    timezone: str
    time: str  # HH:MM format


@dataclass
class Event:
    """Event with type field.
    
    Types:
    - "player_changed_clock": clock was changed (has changed_at)
    - "player_sent_email": email was sent (has recipient, sent_at)
    """
    type: str  # "player_changed_clock" or "player_sent_email"
    changed_at: Optional[str] = None  # HH:MM format for player_changed_clock
    recipient: Optional[str] = None   # For player_sent_email
    sent_at: Optional[str] = None     # HH:MM format for player_sent_email


@dataclass
class StrictState:
    """
    Closed-schema state used for win conditions and validation.
    
    No dynamic keys allowed. Structure is fixed and enforced.
    """
    clock: Clock
    events: list[Event] = field(default_factory=list)


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
            events=[]
        ),
        vibe=VibeState(
            system_config={},
            emails=[],
            notes=[]
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
        events=data["strict"]["events"]
    )
    
    vibe = VibeState(
        system_config=data["vibe"]["system_config"],
        emails=data["vibe"]["emails"],
        notes=data["vibe"]["notes"]
    )
    
    return GameState(strict=strict, vibe=vibe)
