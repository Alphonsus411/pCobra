from pathlib import Path


def _parse_env_assignments(content: str) -> dict[str, str]:
    pares: dict[str, str] = {}
    for linea in content.splitlines():
        texto = linea.strip()
        if not texto or texto.startswith("#") or "=" not in texto:
            continue
        clave, valor = texto.split("=", 1)
        pares[clave.strip()] = valor.strip()
    return pares


def test_env_example_minimo_onboarding_contract():
    env_example = Path(".env.example")
    contenido = env_example.read_text(encoding="utf-8")
    pares = _parse_env_assignments(contenido)

    assert pares == {
        "SQLITE_DB_KEY": "dev-key-change-me",
        "COBRA_DB_PATH": "~/.cobra/sqliteplus/core.db",
        "COBRA_USAR_INSTALL": "0",
        "COBRA_CLI_BOOTSTRAP_PATH": "0",
        "COBRA_LOG_FORMATTER": "text",
    }
