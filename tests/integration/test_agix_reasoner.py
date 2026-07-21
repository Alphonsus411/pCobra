"""Pruebas de integración para ``agix`` y el razonador básico."""

import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

pytest.importorskip("agix")
from agix.reasoning.basic import Reasoner


ROOT = Path(__file__).resolve().parents[2]


def _ejecutar_python(codigo: str) -> subprocess.CompletedProcess[str]:
    entorno = os.environ.copy()
    entorno["PYTHONPATH"] = os.pathsep.join(
        filter(None, (str(ROOT / "src"), entorno.get("PYTHONPATH")))
    )
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(codigo)],
        cwd=ROOT,
        env=entorno,
        capture_output=True,
        text=True,
        check=False,
    )


def test_analizador_importa_distribucion_real_sin_aliases_ficticios():
    resultado = _ejecutar_python(
        """
        import sys

        assert "src.agix" not in sys.modules
        from pcobra.ia import analizador_agix

        assert analizador_agix.Reasoner.__module__ == "agix.reasoning.basic"
        assert analizador_agix.PADState.__module__ == "agix.emotion.emotion_simulator"
        assert "src.agix" not in sys.modules
        """
    )

    assert resultado.returncode == 0, resultado.stderr


def test_analizador_sin_paquete_agix_mantiene_mensaje_estable():
    resultado = _ejecutar_python(
        """
        import importlib.abc
        import sys

        class BloquearAgix(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if fullname == "agix" or fullname.startswith("agix."):
                    raise ModuleNotFoundError(
                        "No module named 'agix'", name="agix"
                    )
                return None

        sys.meta_path.insert(0, BloquearAgix())
        from pcobra.ia.analizador_agix import (
            MENSAJE_DEPENDENCIA_AGIX,
            generar_sugerencias,
        )

        try:
            generar_sugerencias("var x = 5")
        except ImportError as exc:
            assert str(exc) == MENSAJE_DEPENDENCIA_AGIX
        else:
            raise AssertionError("Se esperaba ImportError sin la distribución agix")
        """
    )

    assert resultado.returncode == 0, resultado.stderr


def test_agix_reasoner_selects_best_model():
    evaluations = [
        {"name": "A", "accuracy": 0.8, "interpretability": 0.9},
        {"name": "B", "accuracy": 0.85, "interpretability": 0.7},
        {"name": "C", "accuracy": 0.85, "interpretability": 0.8},
    ]
    result = Reasoner().select_best_model(evaluations)
    assert result["name"] == "C"
    assert "Modelo seleccionado" in result["reason"]
