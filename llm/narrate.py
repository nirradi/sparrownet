"""Output generator for Narrator LLM renderer.

Produces terse, in-universe terminal text for player-facing output.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import logging
from .tools import call_llm, load_model_config, load_prompt

# TODO: Prompt tuning per level
# TODO: Injecting story context later

@dataclass
class NarrationInput:
    intent_type: str
    success: bool
    errors: List[str]
    patch: Optional[Dict[str, Any]] = None

LOG = logging.getLogger(__name__)

MODEL_CFG: Dict[str, Any] = load_model_config(key="narrator")
PROMPT_TPL: str = load_prompt("narrate")

def build_narration_prompt(input: NarrationInput) -> str:
    """
    Construct the LLM prompt for narration, following style and rules.
    """
    lines = []
    lines.append(f"The user issued a {input.intent_type} command.")
    if input.success:
        lines.append("The operation succeeded.")
    else:
        lines.append("The operation failed.")
        if input.errors:
            for err in input.errors:
                lines.append(f"Error: {err}")
    if input.patch:
        for k, v in input.patch.items():
            lines.append(f"{k}: {v}")
    lines.append("Generate the terminal response.")
    return "\n".join(lines)

def generate_narration(input: NarrationInput) -> str:
    """
    Generate a terse, in-universe terminal response for the player using LLM.
    Output is plain text, no meta commentary, no emojis, no explanations.
    """
    prompt = build_narration_prompt(input)
    try:
        raw = call_llm(prompt, MODEL_CFG)
        text = (raw or "").strip()
        # Remove Markdown code block markers and surrounding quotes
        if text.startswith("```") and text.endswith("```"):
            text = text[3:-3].strip()
        for q in ("'''", '"""', "'", '"'):
            if text.startswith(q) and text.endswith(q):
                text = text[len(q):-len(q)].strip()
        return text
    except Exception as exc:
        LOG.error("Narrator LLM failed: %s", exc)
        # Fallback: minimal error message
        return "[narration unavailable]"
