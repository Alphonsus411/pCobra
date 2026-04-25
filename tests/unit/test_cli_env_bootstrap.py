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
    assert any(
        record.levelname == "INFO"
        and "No se encontró .env; se creó automáticamente" in record.getMessage()
        for record in caplog.records
    )
    assert "WARNING: El archivo .env no se cargó" not in caplog.text
    assert "COBRA_DB_PATH" in cli.os.environ


def test_configurar_entorno_falla_si_falta_sqlite_db_key(tmp_path, monkeypatch, caplog):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)

    monkeypatch.setattr(cli, "load_dotenv", lambda **_kwargs: False)
    caplog.set_level("ERROR", logger="pcobra.cli")

    try:
        cli.configurar_entorno()
        raise AssertionError("Se esperaba RuntimeError cuando falta SQLITE_DB_KEY")
    except RuntimeError as exc:
        assert "SQLITE_DB_KEY es obligatoria y está ausente o vacía" in str(exc)
    assert "Falta SQLITE_DB_KEY en el entorno" in caplog.text


def test_configurar_entorno_setea_db_path_por_default_con_sqlite_db_key(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SQLITE_DB_KEY", "clave-segura")
    monkeypatch.delenv("COBRA_DB_PATH", raising=False)
    monkeypatch.setattr(cli, "load_dotenv", lambda **_kwargs: True)

    cli.configurar_entorno()

    assert cli.os.environ["COBRA_DB_PATH"] == cli._DEFAULT_DB_PATH
