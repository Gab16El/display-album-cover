import builtins

import pytest

from launcher.mode import LaunchMode, ask_launch_mode, resolve_launch_mode


def answer_with(monkeypatch, *answers: str) -> LaunchMode:
    replies = iter(answers)
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(replies))
    return ask_launch_mode()


@pytest.mark.parametrize(
    ("answers", "expected"),
    [(("",), "pc"), (("1",), "pc"), (("2",), "phone"), (("3",), "both"), (("x", "9", "2"), "phone")],
)
def test_menu_choices(monkeypatch, answers, expected):
    assert answer_with(monkeypatch, *answers).value == expected


def test_menu_defaults_to_pc_without_input(monkeypatch):
    def no_input(prompt=""):
        raise EOFError

    monkeypatch.setattr(builtins, "input", no_input)
    assert ask_launch_mode() is LaunchMode.PC


def test_flags_skip_the_question():
    assert resolve_launch_mode("phone", False, True) is LaunchMode.PHONE
    assert resolve_launch_mode(None, True, True) is LaunchMode.BOTH
    assert resolve_launch_mode(None, False, False) is LaunchMode.PC


def test_mode_capabilities():
    assert (LaunchMode.PC.serves_lan, LaunchMode.PC.opens_browser) == (False, True)
    assert (LaunchMode.PHONE.serves_lan, LaunchMode.PHONE.opens_browser) == (True, False)
    assert (LaunchMode.BOTH.serves_lan, LaunchMode.BOTH.opens_browser) == (True, True)
