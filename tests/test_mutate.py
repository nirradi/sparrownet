import json

import llm.tools as tools
import llm.mutate as mutate


def test_generate_patch_with_mocked_llm(monkeypatch):
    # Provide a minimal prompt template that will be formatted by generate_patch
    mutate.set_mutator({}, "{intent} {state} {level_context}")

    # Mock the LLM call to return a valid JSON string
    sample = json.dumps({
        "strict": {"player": {"x": 2}},
        "vibe": {"message": "A breeze blows the curtain."},
    })

    # Patch the function actually used by mutate.generate_patch (it imports
    # `call_llm` at module import time), so patch there.
    monkeypatch.setattr(mutate, "call_llm", lambda prompt, cfg: sample)

    class Intent:
        def to_dict(self):
            return {"action": "move", "dir": "east"}

    class State:
        def to_dict(self):
            return {"player": {"x": 1}}

    patch = mutate.generate_patch(Intent(), State(), level_context={})

    assert isinstance(patch, dict)
    assert "strict" in patch and "vibe" in patch
    assert patch["strict"]["player"]["x"] == 2
    assert patch["vibe"]["message"] == "A breeze blows the curtain."
