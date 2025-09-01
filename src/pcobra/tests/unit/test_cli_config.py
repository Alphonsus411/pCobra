from cobra.cli.utils.config import DEFAULTS, load_config

ENV_VARS = [
    "COBRA_LANG",
    "COBRA_DEFAULT_COMMAND",
    "COBRA_LOG_FORMAT",
    "COBRA_PROGRAM_NAME",
]


def _clear_env(monkeypatch):
    for key in ENV_VARS:
        monkeypatch.delenv(key, raising=False)


def test_load_config_from_valid_file(tmp_path, monkeypatch):
    cfg = tmp_path / "cobra-cli.toml"
    cfg.write_text(
        """
language = "en"
default_command = "run"
log_format = "%(levelname)s"
program_name = "cobrax"
"""
    )
    monkeypatch.chdir(tmp_path)
    _clear_env(monkeypatch)

    data = load_config()

    assert data == {
        "language": "en",
        "default_command": "run",
        "log_format": "%(levelname)s",
        "program_name": "cobrax",
    }


def test_load_config_defaults_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _clear_env(monkeypatch)

    data = load_config()

    assert data == DEFAULTS


def test_load_config_with_partial_config(tmp_path, monkeypatch):
    cfg = tmp_path / "cobra-cli.toml"
    cfg.write_text("language = \"en\"")
    monkeypatch.chdir(tmp_path)
    _clear_env(monkeypatch)

    data = load_config()

    assert data["language"] == "en"
    assert data["default_command"] == DEFAULTS["default_command"]
    assert data["log_format"] == DEFAULTS["log_format"]
    assert data["program_name"] == DEFAULTS["program_name"]


def test_load_config_with_corrupt_file(tmp_path, monkeypatch):
    cfg = tmp_path / "cobra-cli.toml"
    cfg.write_text("language = 'en' [")
    monkeypatch.chdir(tmp_path)
    _clear_env(monkeypatch)

    data = load_config()

    assert data == DEFAULTS
