"""Smoke E2E del contrato POO desde fuente Cobra (Task 42L)."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import re
import shutil
import subprocess

import pytest

from pcobra.cobra.backends.javascript_adapter import JavaScriptAdapter
from pcobra.cobra.backends.python_adapter import PythonAdapter
from pcobra.cobra.backends.rust_adapter import RustAdapter
from pcobra.cobra.core.parsing import parsear_codigo_resuelto
from pcobra.core.interpreter import InterpretadorCobra

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[2]
NATIVOS_JAVASCRIPT = RAIZ_REPOSITORIO / "src" / "pcobra" / "core" / "nativos"

FUENTE_CONTRACTUAL = """clase Persona:
    metodo inicializar(este, nombre):
        atributo este nombre = nombre

    metodo saludar(este):
        imprimir "Hola " + atributo este nombre
fin

var persona = Persona("Adolfo")
persona.saludar()
"""


def _ast_contractual():
    return parsear_codigo_resuelto(FUENTE_CONTRACTUAL, usar_cache=False)


def test_runtime_ejecuta_el_smoke_poo_contractual_desde_fuente(capsys):
    InterpretadorCobra().ejecutar_ast(_ast_contractual())

    assert capsys.readouterr().out.strip() == "Hola Adolfo"


def test_python_ejecuta_el_smoke_poo_contractual_desde_fuente():
    codigo = PythonAdapter().compile(_ast_contractual())
    salida = StringIO()

    with redirect_stdout(salida):
        exec(codigo, {})

    assert salida.getvalue().strip() == "Hola Adolfo"


def test_javascript_ejecuta_el_smoke_poo_contractual_con_nativos_reales(tmp_path):
    node = shutil.which("node")
    if node is None:
        pytest.skip("node no está disponible")

    assert "node-fetch" not in (NATIVOS_JAVASCRIPT / "io.js").read_text(
        encoding="utf-8"
    )
    assert "node-fetch" not in (NATIVOS_JAVASCRIPT / "red.js").read_text(
        encoding="utf-8"
    )
    assert "from 'uuid'" not in (NATIVOS_JAVASCRIPT / "seguridad.js").read_text(
        encoding="utf-8"
    )

    (tmp_path / "programa.mjs").write_text(
        JavaScriptAdapter().compile(_ast_contractual()), encoding="utf-8"
    )
    (tmp_path / "uuid.mjs").write_text(
        "import { generar_uuid } from './nativos/seguridad.js';\n"
        "console.log(generar_uuid());\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text('{"type":"module"}\n', encoding="utf-8")
    shutil.copytree(NATIVOS_JAVASCRIPT, tmp_path / "nativos")

    proceso = subprocess.run(
        [node, "programa.mjs"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert proceso.stdout.strip() == "Hola Adolfo"
    assert proceso.stderr == ""

    uuid = subprocess.run(
        [node, "uuid.mjs"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
        uuid.stdout.strip(),
    )


def test_rust_diagnostica_el_smoke_fuera_de_su_subconjunto_poo():
    with pytest.raises(NotImplementedError, match="atributos de instancia"):
        RustAdapter().compile(_ast_contractual())
