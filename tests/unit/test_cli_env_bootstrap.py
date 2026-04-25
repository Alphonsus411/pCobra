from pathlib import Path

import pcobra.cli as cli


def test_configurar_entorno_autocrea_env_desde_example(tmp_path, monkeypatch, caplog):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.delenv("COBRA_DB_PATH", raising=False)

    env_example = tmp_path / ".env.example"
    env_example.write_text("SQLITE_DB_KEY=dev-key\n", encoding="utf-8")

    def _fake_load_dotenv(*, dotenv_path=None):
        assert dotenv_path == Path(".env")
        for line in Path(dotenv_path).read_text(encoding="utf-8").splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            monkeypatch.setenv(key.strip(), value.strip())
        return True

    monkeypatch.setattr(cli, "load_dotenv", _fake_load_dotenv)

    caplog.set_level("INFO", logger="pcobra.cli")
    cli.configurar_entorno()

    env_file = tmp_path / ".env"
    assert env_file.exists()
    assert env_file.read_text(encoding="utf-8") == env_example.read_text(encoding="utf-8")
    assert "No se encontró .env; se creó automáticamente" in caplog.text
    assert "COBRA_DB_PATH" in cli.os.environ


def test_configurar_entorno_registra_error_si_falta_sqlite_db_key(tmp_path, monkeypatch, caplog):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)

    monkeypatch.setattr(cli, "load_dotenv", lambda **_kwargs: False)

    caplog.set_level("ERROR", logger="pcobra.cli")
    cli.configurar_entorno()

    assert "Falta SQLITE_DB_KEY" in caplog.text
