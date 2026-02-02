"""Helper utilities for LLM interactions and prompt loading.

This module centralizes loading model configs, prompt templates, and
calling the `llm.client` adapter. Keep logic small and robust so other
modules (like `llm.mutate`) can remain focused.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

LOG = logging.getLogger(__name__)


# No default prompt fallback: prompt file must exist and contain usable text.


def load_model_config(config_file: Path = Path("config") / "models.dev.yaml", key: str = "mutator") -> Dict[str, Any]:
    try:
        if not config_file.exists():
            return {}
        # Import yaml lazily to avoid hard dependency during quick runs.
        try:
            import yaml  # type: ignore
        except Exception:
            LOG.debug("PyYAML not installed, skipping config parse")
            return {}

        cfg = yaml.safe_load(config_file.read_text()) or {}
        if isinstance(cfg, dict):
            return cfg.get(key, {}) or {}
    except Exception:
        LOG.debug("Failed to load model config %s", config_file, exc_info=True)
    return {}


def load_prompt(prompt_name: str = "mutate") -> str:
    """Load a prompt template from `llm/prompts/{prompt_name}.yml` or `.yaml`.
    Raises RuntimeError if no prompt file is available or parse fails.
    """
    base = Path("llm") / "prompts" / prompt_name
    for suf in (".yml", ".yaml"):
        p = base.with_suffix(suf)
        try:
            if p.exists():
                raw = p.read_text()
                # Try YAML parse if available
                try:
                    import yaml  # type: ignore
                    parsed = yaml.safe_load(raw)
                    if isinstance(parsed, dict) and "prompt" in parsed and isinstance(parsed["prompt"], str):
                        return parsed["prompt"].strip()
                except Exception:
                    LOG.debug("PyYAML not available or parse failed for %s", p, exc_info=True)
                return raw.strip()
        except Exception:
            LOG.debug("Failed to read prompt %s", p, exc_info=True)
    raise RuntimeError(f"Prompt template not found for '{prompt_name}' (looked for {base}.yml/.yaml)")


def call_llm(prompt: str, model_cfg: Dict[str, Any]) -> Optional[str]:
    """Call the configured `llm.client.generate` and return its result.

    This function propagates exceptions from the client; callers may
    choose to catch them. It no longer silently returns `None` when the
    client is missing or misconfigured.
    """
    import llm.client as client  # type: ignore

    # Expect `generate(prompt, model_cfg)` to be present.
    if not hasattr(client, "generate"):
        raise RuntimeError("llm.client does not implement 'generate'")

    return client.generate(prompt, model_cfg)
