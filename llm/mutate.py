"""State mutation LLM.

This module translates an Intent + GameState + optional level_context
into a proposal `patch` dict suitable for `engine.patch.apply_patch`.

Design constraints enforced here:
- Never mutate state directly.
- Never decide win conditions.
- Only propose patches (keys: "strict", "vibe").

The implementation is defensive: failures, invalid LLM output, timeouts
or missing client implementations will return an empty patch (`{}`).
Raw LLM outputs are logged at DEBUG level for troubleshooting.

The module attempts to load the mutator model config from
`config/models.dev.yaml` under the `mutator` key and a prompt template
from `llm/prompts/mutate.yaml`. If those are missing, sensible
fallbacks are used.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, Optional

from .tools import call_llm, load_model_config, load_prompt
from engine.state import strict_state_schema

LOG = logging.getLogger(__name__)


# Initialize model config and prompt at import time so `generate_patch`
# remains focused and deterministic during calls. Tests can override
# these with `set_mutator`.
MODEL_CFG: Dict[str, Any] = load_model_config()
PROMPT_TPL: str = load_prompt("mutate")


def set_mutator(model_cfg: Dict[str, Any], prompt_tpl: str) -> None:
	"""Override the mutator configuration and prompt (useful for tests).

	Both arguments may be empty-ish; function is defensive.
	"""
	global MODEL_CFG, PROMPT_TPL
	MODEL_CFG = model_cfg or {}
	PROMPT_TPL = prompt_tpl or PROMPT_TPL


def resolve_intent_placeholders(patch: Dict[str, Any], intent: Any) -> Dict[str, Any]:
	"""Resolve ${intent.<field>} placeholders in patch with actual intent values.

	Recursively walks through the patch dict (strict and vibe) and replaces
	any string matching the pattern ${intent.<field>} with getattr(intent, <field>).
	Preserves patch structure (keys, lists, dicts). Returns a new dict.

	Args:
		patch: The patch dict to process.
		intent: The intent object to resolve from.

	Returns:
		A new patch dict with placeholders resolved, or the original if no placeholders found.
	"""
	def _resolve_value(val: Any) -> Any:
		if isinstance(val, str):
			# Look for ${intent.<field>} pattern
			match = re.match(r"^\$\{intent\.(\w+)\}$", val)
			if match:
				field = match.group(1)
				try:
					return getattr(intent, field, val)  # fallback to original if missing
				except Exception:
					LOG.debug("Could not resolve intent.%s", field, exc_info=True)
					return val
			return val
		elif isinstance(val, dict):
			return {k: _resolve_value(v) for k, v in val.items()}
		elif isinstance(val, list):
			return [_resolve_value(item) for item in val]
		else:
			return val

	return _resolve_value(patch)


def _extract_json(text: str) -> Optional[str]:
	"""Extract JSON from text, handling markdown code fences."""
	text = (text or "").strip()
	
	# If it's pure JSON, return it
	if text.startswith("{") and text.endswith("}"):
		return text
	
	# Try to extract from markdown code fences (```json ... ```)
	if "```" in text:
		parts = text.split("```")
		for part in parts:
			part = part.strip()
			# Skip language identifier line (e.g., "json")
			if part.startswith("json"):
				part = part[4:].strip()
			if part.startswith("{") and part.endswith("}"):
				return part
	
	# Try to find first balanced brace pair
	brace_start = text.find("{")
	if brace_start == -1:
		return None
	depth = 0
	for i in range(brace_start, len(text)):
		if text[i] == "{":
			depth += 1
		elif text[i] == "}":
			depth -= 1
			if depth == 0:
				return text[brace_start : i + 1]
	return None


def _serialize_state(state: Any) -> Dict[str, Any]:
	"""Return a deeply JSON-serializable representation of state.

	Recursively converts nested objects to dicts to ensure JSON compatibility.
	"""
	def _to_dict(obj: Any) -> Any:
		if obj is None or isinstance(obj, (str, int, float, bool)):
			return obj
		if isinstance(obj, dict):
			return {k: _to_dict(v) for k, v in obj.items()}
		if isinstance(obj, (list, tuple)):
			return [_to_dict(item) for item in obj]
		if hasattr(obj, "to_dict") and callable(obj.to_dict):
			try:
				return _to_dict(obj.to_dict())
			except Exception:
				pass
		if hasattr(obj, "__dict__"):
			try:
				return {k: _to_dict(v) for k, v in vars(obj).items() if not k.startswith("_")}
			except Exception:
				pass
		# Fallback for non-serializable objects
		return str(obj)

	try:
		if state is None:
			return {}
		return _to_dict(state) or {}
	except Exception:
		LOG.debug("Error serializing state", exc_info=True)
	return {"repr": str(state)}



def _filter_strict_patch(patch: Dict[str, Any], intent: Any) -> Dict[str, Any]:
    """Filter strict fields from patch to only those allowed by intent.strict_targets."""
    allowed = set(getattr(intent, 'strict_targets', []))
    if "strict" in patch and isinstance(patch["strict"], dict):
        original = set(patch["strict"].keys())
        filtered = {k: v for k, v in patch["strict"].items() if k in allowed}
        removed = original - set(filtered.keys())
        if removed:
            LOG.debug("Intent %r not allowed to modify strict fields: %r; removing.", getattr(intent, "type", None), list(removed))
        patch = dict(patch)
        patch["strict"] = filtered
    # If no allowed strict targets, ensure strict is empty dict
    if not allowed:
        patch["strict"] = {}
    return patch

def generate_patch(intent: Any, state: Any, level_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
	"""Generate a patch dict from `intent` and `state` using an LLM.

	This function is defensive about LLM output (malformed JSON etc.)
	but it does NOT swallow client-configuration errors. If the LLM
	client is not installed or misconfigured, callers will get an
	exception so they can fix their environment.
	"""
	level_context = level_context or {}

	# Use module-level config/prompt (can be overridden in tests)
	model_cfg = MODEL_CFG
	prompt_tpl = PROMPT_TPL

	# Prepare minimal serializations
	ser_intent = intent.to_dict() if hasattr(intent, "to_dict") else (intent if isinstance(intent, dict) else {"repr": str(intent)})
	ser_state = _serialize_state(state)
	strict_targets = getattr(intent, "strict_targets", [])
	strict_schema = strict_state_schema()

	# Substitute placeholders directly instead of using .format() to avoid 
	# interpreting literal braces in the prompt template
	intent_json = json.dumps(ser_intent)
	state_json = json.dumps(ser_state)
	context_json = json.dumps(level_context)
	strict_targets_json = json.dumps(strict_targets)
	strict_schema_json = json.dumps(strict_schema, indent=2)

	# log intent before prompt
	LOG.debug("Generating patch for intent: %s", intent_json)
	prompt = prompt_tpl.replace("{intent}", intent_json)\
		.replace("{state}", state_json)\
		.replace("{level_context}", context_json)\
		.replace("{strict_targets}", strict_targets_json)\
		.replace("{strict_schema}", strict_schema_json)

	# Call the LLM (may raise if client not available)
	raw = call_llm(prompt, model_cfg)

	LOG.debug("Raw mutator LLM output: %s", raw)

	# Parse JSON defensively
	parsed = None
	try:
		parsed = json.loads(raw)
	except Exception:
		# try to extract JSON substring
		jtxt = _extract_json(raw or "")
		if jtxt:
			try:
				parsed = json.loads(jtxt)
			except Exception:
				LOG.debug("Failed to parse extracted JSON", exc_info=True)

	if not isinstance(parsed, dict):
		LOG.debug("Parsed LLM output is not an object/dict")
		return {}

	# Filter to allowed top-level keys and ensure values are dicts
	patch: Dict[str, Any] = {}
	for k in ("strict", "vibe"):
		if k in parsed and isinstance(parsed[k], dict):
			patch[k] = parsed[k]

	# Resolve ${intent.<field>} placeholders before returning
	patch = resolve_intent_placeholders(patch, intent)

	# Filter strict patch to only allowed keys
	patch = _filter_strict_patch(patch, intent)

	return patch

