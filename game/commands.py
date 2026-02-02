"""Intent parsing for terminal input.

This module classifies free-form player input into a small, strict
set of Intent objects. It contains no game-state mutation or validation.

Phase 1 supported intents:
- SHOW_CONFIG
- SET_CLOCK (params: offset_hours: int)
- READ_EMAIL
- SEND_EMAIL (params: recipient: str, body: str)

The parsing is intentionally lightweight and heuristic-based so it's
easy to extend and unit-test.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional


class IntentType(Enum):
	SHOW_CONFIG = auto()
	SET_CLOCK = auto()
	READ_EMAIL = auto()
	SEND_EMAIL = auto()
	UNKNOWN = auto()


@dataclass(frozen=True)
class Intent:
	type: IntentType
	params: Dict[str, Any]
	confidence: float


def _parse_offset_hours(text: str) -> Optional[int]:
	"""Extract an integer hour offset from text.

	Examples matched: '+2', '+02:00', 'utc+2', '-3', 'UTC -03:00'

	Returns the integer hours (minutes are ignored). Returns None if no
	suitable offset is found.
	"""
	# Look for patterns like +02, -3, +02:00, optionally with utc/gmt prefix
	m = re.search(r'([+-])\s*(\d{1,2})(?::\d{2})?', text, flags=re.IGNORECASE)
	if not m:
		return None
	sign = -1 if m.group(1).strip().startswith('-') else 1
	try:
		hours = int(m.group(2))
	except ValueError:
		return None
	return sign * hours


def _extract_send_email(text: str) -> Optional[Dict[str, str]]:
	"""Heuristically extract recipient and body for SEND_EMAIL.

	Returns a dict with keys 'recipient' and 'body' if some recipient-like
	token is found. Otherwise returns None.
	"""
	# Try patterns like: "send email to ops: body..." or "email admin that ..."
	patterns = [
		r'send (?:an )?(?:email )?to (?P<recipient>[\w@.\-]+)(?:[,:]?\s*(?P<body>.+))?$',
		r'email (?P<recipient>[\w@.\-]+) (?:that|saying|:|,)?\s*(?P<body>.+)$',
		r'email (?P<body>.+) to (?P<recipient>[\w@.\-]+)$',
	]
	for p in patterns:
		m = re.search(p, text, flags=re.IGNORECASE)
		if m:
			recipient = m.groupdict().get('recipient') or ''
			body = m.groupdict().get('body') or ''
			return {'recipient': recipient.strip(), 'body': body.strip()}

	# Fallback: if the command starts with 'email' and contains some phrase,
	# treat the first token as recipient if it looks like a name/address.
	m = re.search(r'^email\s+(?P<rest>.+)$', text, flags=re.IGNORECASE)
	if m:
		rest = m.group('rest').strip()
		# If rest starts with a single word recipient
		if ' ' in rest:
			first, tail = rest.split(' ', 1)
			if re.match(r'^[\w@.\-]+$', first):
				return {'recipient': first.strip(), 'body': tail.strip()}
		# No clear recipient found; do not claim extraction
	return None


def parse_intent(user_input: str) -> Intent:
	"""Parse free-form user input into a structured Intent.

	The function never raises; unknown or unclassifiable inputs are
	returned as IntentType.UNKNOWN with low confidence.
	"""
	raw = (user_input or '').strip()
	low = raw.lower()

	if not raw:
		return Intent(IntentType.UNKNOWN, {}, 0.0)

	# 1) SHOW_CONFIG detection
	if re.search(r'\b(show|print)\b.*\bconfig(uration)?\b', low) or re.fullmatch(r'config|configuration', low):
		return Intent(IntentType.SHOW_CONFIG, {}, 0.95)

	# 2) READ_EMAIL detection
	if re.search(r'\b(open|read|show)\b.*\b(mail|email|inbox)\b', low) or low in {'inbox'}:
		return Intent(IntentType.READ_EMAIL, {}, 0.9)

	# 3) SEND_EMAIL detection (must come before SET_CLOCK to avoid misclassifying emails mentioning 'clock')
	if re.search(r'\b(send|email)\b', low):
		extract = _extract_send_email(raw)
		if extract:
			# If recipient present but body empty, body should be empty string
			return Intent(IntentType.SEND_EMAIL, {'recipient': extract.get('recipient', ''), 'body': extract.get('body', '')}, 0.9)
		# Could not extract recipient confidently; still classify as send intent but low confidence
		# Always include raw input for downstream/fallback LLM
		if 'send' in low:
			return Intent(IntentType.SEND_EMAIL, {'recipient': '', 'body': raw, 'raw': raw}, 0.4)
		# fallback: if it looks like an email command but not parseable, still return intent with raw
		return Intent(IntentType.SEND_EMAIL, {'raw': raw}, 0.3)

	# 4) SET_CLOCK detection
	if 'clock' in low or 'system time' in low or 'utc' in low or 'gmt' in low:
		offset = _parse_offset_hours(low)
		if offset is not None:
			return Intent(IntentType.SET_CLOCK, {'offset_hours': offset}, 0.92)
		# If we can't parse offset, still include raw input for downstream use
		if re.search(r'\bset\b.*\bclock\b', low) or re.search(r'\bset\b.*\bsystem time\b', low):
			return Intent(IntentType.SET_CLOCK, {'raw': raw}, 0.5)
		# fallback: if it looks like a clock command but not parseable, still return intent with raw
		return Intent(IntentType.SET_CLOCK, {'raw': raw}, 0.3)

	# Unknown intent
	return Intent(IntentType.UNKNOWN, {}, 0.0)


__all__ = ['IntentType', 'Intent', 'parse_intent']

