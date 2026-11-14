import pytest

from triage_copilot import main


def test_main_prints_greeting(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    captured = capsys.readouterr()
    assert "triage-copilot" in captured.out
