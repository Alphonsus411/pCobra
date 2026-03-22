from __future__ import annotations

from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

import pcobra  # noqa: F401 - asegura el registro de paquetes
from cobra.cli.cli import main
from cobra.cli.utils import messages


def _run_cli(arguments: list[str]) -> tuple[int, str]:
    with messages.color_disabled():
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            try:
                exit_code = main(["--no-color", *arguments])
            except SystemExit as exc:
                exit_code = exc.code if isinstance(exc.code, int) else 1
    return exit_code, stdout.getvalue()


@pytest.mark.timeout(5)
def test_regresion_cli_compilar_rechaza_backend_hololang_con_mensaje_de_choices(
    tmp_path: Path,
) -> None:
    # Regresión: `hololang` solo puede aparecer como IR/pipeline interno, no
    # como target público vigente de `cobra compilar`.
    archivo = tmp_path / "saludo.co"
    archivo.write_text('imprimir("hola")\n', encoding="utf-8")

    exit_code, salida = _run_cli(["compilar", str(archivo), "--backend", "hololang"])

    salida_normalizada = salida.lower()
    assert exit_code == 2
    assert "target no soportado" in salida_normalizada
    assert "hololang" in salida_normalizada
    assert "--backend" in salida_normalizada
    assert "python" in salida_normalizada
    assert "asm" in salida_normalizada


@pytest.mark.timeout(5)
def test_regresion_cli_transpilar_inverso_rechaza_origen_hololang_con_mensaje_de_choices(
    tmp_path: Path,
) -> None:
    # Regresión: `hololang` no forma parte del scope reverse oficial definido
    # en `reverse/policy.py`; este test verifica rechazo, no soporte.
    archivo = tmp_path / "saludo.py"
    archivo.write_text('print("hola")\n', encoding="utf-8")

    exit_code, salida = _run_cli(
        [
            "transpilar-inverso",
            str(archivo),
            "--origen",
            "hololang",
            "--destino",
            "python",
        ]
    )

    salida_normalizada = salida.lower()
    assert exit_code == 2
    assert "lenguaje de origen no soportado para transpilación inversa" in salida_normalizada
    assert "hololang" in salida_normalizada
    assert "--origen" in salida_normalizada
    assert "python" in salida_normalizada
    assert "javascript" in salida_normalizada
    assert "java" in salida_normalizada
