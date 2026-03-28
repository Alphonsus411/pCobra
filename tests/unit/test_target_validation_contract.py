import argparse
from io import StringIO
from unittest.mock import patch

import pytest

from cobra.cli.cli import main
from pcobra.cobra.cli.target_policies import parse_target
from pcobra.cobra.semantico import mod_validator


def test_api_parse_target_valido_canonico() -> None:
    assert parse_target("python") == "python"


def test_api_parse_target_alias_permitido_deprecado() -> None:
    with pytest.deprecated_call(match="Alias de target en desuso"):
        assert parse_target("c++") == "cpp"


def test_api_parse_target_invalido_muestra_lista_exacta_con_tiers() -> None:
    with pytest.raises(argparse.ArgumentTypeError) as exc:
        parse_target("fantasy")
    mensaje = str(exc.value)
    assert "python=tier1" in mensaje
    assert "asm=tier2" in mensaje


def test_cli_compilar_target_invalido_muestra_lista_exacta_con_tiers(tmp_path) -> None:
    archivo = tmp_path / "demo.co"
    archivo.write_text("mostrar(\"hola\")\n", encoding="utf-8")

    with patch("sys.stdout", new_callable=StringIO) as out:
        with pytest.raises(SystemExit) as exc:
            main(["compilar", str(archivo), "--tipo=fantasy"])
    assert exc.value.code == 2
    salida = out.getvalue()
    assert "python=tier1" in salida
    assert "asm=tier2" in salida


def test_mod_validator_rechaza_required_targets_fuera_de_lista(monkeypatch) -> None:
    monkeypatch.setattr(
        mod_validator.module_map,
        "get_toml_map",
        lambda: {"project": {"required_targets": ["python", "fantasy"]}},
    )
    with pytest.raises(ValueError) as exc:
        mod_validator._required_targets_from_policy()
    mensaje = str(exc.value)
    assert "target no permitido" in mensaje
    assert "python=tier1" in mensaje
    assert "asm=tier2" in mensaje
