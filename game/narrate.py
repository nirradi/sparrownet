from dataclasses import dataclass
from typing import Literal

@dataclass
class NarrationResult:
	text: str
	source: Literal["rules", "llm"]

from llm.narrate import NarrationInput, generate_narration

def narrate(outcome) -> NarrationResult:
    """Narrator: rules for unknown command, LLM for all else."""
    # Rule 1: Unknown command
    if outcome.intent_type == "UNKNOWN":
        return NarrationResult(text="command not found", source="rules")

    # For all other cases, invoke the LLM narrator
    input_obj = NarrationInput(
        intent_type=outcome.intent_type,
        success=outcome.success,
        errors=[],
        patch=getattr(outcome, "patch", None) if outcome.success else None,
    )
    narration = generate_narration(input_obj)
    return NarrationResult(text=narration, source="llm")