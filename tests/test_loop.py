"""Tests for the main game loop."""

import pytest
from io import StringIO
from unittest.mock import patch
from game.loop import main


def test_full_game_loop_sequence_via_main():
    """End-to-end test: run the actual main() loop through win condition."""
    
    # Simulate user input: show config, read email, set clock, send email, then exit
    user_inputs = [
        "show config",
        "read email",
        "set clock +05:00",
        "send email to admin@example.com: urgent issue",
        "exit",
    ]
    
    input_iter = iter(user_inputs)
    
    def mock_input(prompt=""):
        return next(input_iter)
    
    output = StringIO()
    
    with patch('builtins.input', side_effect=mock_input):
        with patch('sys.stdout', output):
            try:
                main()
            except StopIteration:
                # Expected: we ran out of inputs
                pass
    
    # Verify output contains expected state changes
    output_text = output.getvalue()
    assert "05:00" in output_text, "Clock should be set to 05:00 in output"
    assert "success" in output_text.lower(), "Should display success/win message"
