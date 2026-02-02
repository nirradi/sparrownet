import pytest

from game.commands import parse_intent, IntentType


@pytest.mark.parametrize("inp", [
    "show config",
    "print system configuration",
    "config",
])
def test_show_config(inp):
    intent = parse_intent(inp)
    assert intent.type == IntentType.SHOW_CONFIG
    assert 0.5 <= intent.confidence <= 1.0


@pytest.mark.parametrize("inp,expected", [
    ("set clock +2", 2),
    ("clock set +02:00", 2),
    ("set system time to utc+2", 2),
    ("set clock -3", -3),
])
def test_set_clock_with_offset(inp, expected):
    intent = parse_intent(inp)
    assert intent.type == IntentType.SET_CLOCK
    assert 'offset_hours' in intent.params
    assert intent.params['offset_hours'] == expected
    assert 0.5 <= intent.confidence <= 1.0


@pytest.mark.parametrize("inp", [
    "set clock to banana",
    "set system time to mars",
    "clock set to ???",
])
def test_set_clock_unparsed_has_raw(inp):
    intent = parse_intent(inp)
    assert intent.type == IntentType.SET_CLOCK
    assert 'raw' in intent.params
    assert inp in intent.params['raw']
    assert intent.confidence <= 0.5


@pytest.mark.parametrize("inp", ["read email", "open inbox", "inbox"])
def test_read_email(inp):
    intent = parse_intent(inp)
    assert intent.type == IntentType.READ_EMAIL
    assert 0.5 <= intent.confidence <= 1.0


@pytest.mark.parametrize("inp,recipient_part,body_part", [
    ("send email to ops: please restart the service", "ops", "please restart"),
    ("email admin that the clock is fixed", "admin", "clock is fixed"),
    ("email ops please check", "ops", "please check"),
])
def test_send_email(inp, recipient_part, body_part):
    intent = parse_intent(inp)
    assert intent.type == IntentType.SEND_EMAIL
    # recipient may be exact token or contain it; check substring
    recipient = intent.params.get('recipient', '')
    body = intent.params.get('body', '')
    assert recipient_part in recipient or recipient_part == recipient
    assert body_part in body
    assert 0.3 <= intent.confidence <= 1.0


@pytest.mark.parametrize("inp", [
    "send email about the weather",
    "email just a note",
    "send email banana",
])
def test_send_email_unparsed_has_raw(inp):
    intent = parse_intent(inp)
    assert intent.type == IntentType.SEND_EMAIL
    # If recipient/body are not extracted, 'raw' must be present
    if intent.confidence < 0.9:
        assert 'raw' in intent.params
        assert inp in intent.params['raw']
    # If recipient/body are extracted, 'raw' is not required
    else:
        assert 'recipient' in intent.params
        assert 'body' in intent.params


def test_unknown_and_empty():
    assert parse_intent("").type == IntentType.UNKNOWN
    assert parse_intent("foobar something").type in (IntentType.UNKNOWN,)
