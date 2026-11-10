from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_demo_end_to_end_without_credentials(monkeypatch):
    monkeypatch.delenv("BHARATCODE_API_KEY", raising=False)
    app = AppTest.from_file(str(Path(__file__).resolve().parent.parent / "app.py"), default_timeout=30).run()
    assert not app.exception
    next(button for button in app.button if button.label == "Try Demo").click().run()
    assert not app.exception
    assert app.session_state["report"].mode == "demo"
    assert len(app.session_state["report"].issues) == 10
    assert len(app.metric) == 5
    assert any("DEMO" in warning.value for warning in app.warning)
    app.text_input[1].set_value("nonexistent query").run()
    assert not app.exception
    assert any("0 issues match" in caption.value for caption in app.caption)


def test_failure_keeps_ui_usable(monkeypatch):
    from bharatforge.config import Settings
    monkeypatch.setattr(Settings, "from_env", classmethod(lambda cls: cls()))
    app = AppTest.from_file(str(Path(__file__).resolve().parent.parent / "app.py"), default_timeout=30).run()
    app.text_input[0].set_value("owner/repo")
    next(button for button in app.button if button.label == "Analyze Repository").click().run()
    assert not app.exception
    assert any("BHARATCODE_API_KEY" in error.value for error in app.error)
    next(button for button in app.button if button.label == "Try Demo").click().run()
    assert not app.exception and app.session_state["report"].mode == "demo"
