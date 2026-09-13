"""Regresión dedicada de los casos normativos de CORE Audit, fase 1.

Los ``xfail`` documentan cortes conocidos de la ruta fuente→destino. No se
construyen nodos AST a mano para aparentar soporte que el Parser no ofrece.
"""

from __future__ import annotations

import ast
import shutil
import subprocess

import pytest

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.cobra.backends.javascript_adapter import JavaScriptAdapter
from pcobra.cobra.backends.python_adapter import PythonAdapter
from pcobra.cobra.backends.rust_adapter import RustAdapter
from pcobra.cobra.core import Lexer, Parser
from pcobra.core.ast_nodes import NodoUsar
from tests.utils.runtime import execute_transpiled_code


TRANSPILERS = {
    "python": PythonAdapter,
    "javascript": JavaScriptAdapter,
    "rust": RustAdapter,
}


def _parsear(codigo: str) -> list:
    return Parser(Lexer(codigo).tokenizar()).parsear()


def _compilar(backend: str, nodos: list) -> str:
    return TRANSPILERS[backend]().compile(nodos)


def _verificar_destino(backend: str, codigo: str, tmp_path) -> None:
    """Comprueba el destino sin confundir herramienta ausente con un fallo."""
    if backend == "python":
        ast.parse(codigo)
        return

    if backend == "javascript":
        node = shutil.which("node")
        if node is None:
            pytest.skip("NO APLICA: node no está disponible")
        destino = tmp_path / "audit.js"
        destino.write_text(codigo, encoding="utf-8")
        subprocess.run([node, "--check", str(destino)], check=True)
        return

    rustc = shutil.which("rustc")
    if rustc is None:
        pytest.skip("NO APLICA: rustc no está disponible")
    destino = tmp_path / "audit.rs"
    destino.write_text(
        "mod corelibs {}\nmod standard_library {}\n" + codigo,
        encoding="utf-8",
    )
    subprocess.run(
        [rustc, "--crate-type", "lib", str(destino)],
        check=True,
        cwd=tmp_path,
    )


@pytest.mark.parametrize("backend", PUBLIC_BACKENDS)
def test_01_usar_forma_normativa_compila_en_destinos_publicos(backend, tmp_path):
    """TEST 1: ``usar CADENA`` alcanza y valida los tres destinos públicos."""
    nodos = _parsear('usar "texto"')
    assert nodos == [NodoUsar("texto")]

    codigo = _compilar(backend, nodos)
    _verificar_destino(backend, codigo, tmp_path)

    if backend == "python":
        # Python es el único backend que materializa hoy el runtime de ``usar``.
        assert execute_transpiled_code(backend, codigo, tmp_path) == ""


@pytest.mark.parametrize("backend", PUBLIC_BACKENDS)
def test_02_desde_usar_no_aplica_sin_contrato_normativo(backend):
    """TEST 2: el Libro no define ``desde ... usar ...``; no se inventa sintaxis."""
    pytest.skip(
        f"NO APLICA ({backend}): §3.6 solo publica `usar CADENA` y el Parser "
        "no admite `desde ... usar ...`"
    )


CLASE_CON_OBJETO = """
clase Persona:
    metodo __init__(self, nombre):
        atributo self nombre = nombre
    fin

    metodo saludar(self):
        imprimir(atributo self nombre)
    fin
fin
var persona = Persona("Ada")
persona.saludar()
"""


@pytest.mark.xfail(
    strict=True,
    reason=(
        "ROTO: la fuente no produce NodoInstancia/NodoLlamadaMetodo; "
        "constructor, atributo y llamada no tienen ruta pública completa"
    ),
)
@pytest.mark.parametrize("backend", PUBLIC_BACKENDS)
def test_03_clase_constructor_atributo_metodo_e_instancia(backend, tmp_path):
    """TEST 3: exige comportamiento, no fragmentos del código generado."""
    nodos = _parsear(CLASE_CON_OBJETO)
    codigo = _compilar(backend, nodos)
    _verificar_destino(backend, codigo, tmp_path)
    assert execute_transpiled_code(backend, codigo, tmp_path).strip() == "Ada"


HERENCIA_SIMPLE = """
clase Base:
    metodo valor(self):
        retorno 7
    fin
fin
clase Derivada(Base):
fin
var objeto = Derivada()
imprimir(objeto.valor())
"""


@pytest.mark.xfail(
    strict=True,
    reason=(
        "PARCIAL/ROTO: el Libro incluye herencia en el diseño, pero la llamada "
        "heredada no atraviesa el flujo canónico y Rust no modela la base"
    ),
)
@pytest.mark.parametrize("backend", PUBLIC_BACKENDS)
def test_04_herencia_simple_con_resultado_observable(backend, tmp_path):
    """TEST 4: caso incluido porque Libro y Parser demuestran herencia."""
    nodos = _parsear(HERENCIA_SIMPLE)
    codigo = _compilar(backend, nodos)
    _verificar_destino(backend, codigo, tmp_path)
    assert execute_transpiled_code(backend, codigo, tmp_path).strip() == "7"


# No hay TEST 5 positivo: el Libro no publica ``super`` ni un contrato de
# override. Convertir construcciones del lenguaje anfitrión en Cobra violaría
# la regla de no inventar sintaxis; el estado NO APLICA queda registrado en el
# informe de auditoría.
