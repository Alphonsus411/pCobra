import pytest

from pcobra.core.ast_nodes import (
    NodoGraficar,
    NodoHolobit,
    NodoIdentificador,
    NodoProyectar,
    NodoTransformar,
    NodoValor,
)
from pcobra.cobra.transpilers.transpiler.to_asm import TranspiladorASM
from pcobra.cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from pcobra.cobra.transpilers.transpiler.to_go import TranspiladorGo
from pcobra.cobra.transpilers.transpiler.to_java import TranspiladorJava
from pcobra.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
from pcobra.cobra.transpilers.transpiler.to_rust import TranspiladorRust
from pcobra.cobra.transpilers.transpiler.to_wasm import TranspiladorWasm


@pytest.fixture()
def ast_holobit_runtime():
    return [
        NodoHolobit("hb", [1, 2, 3]),
        NodoProyectar(NodoIdentificador("hb"), NodoValor("2d")),
        NodoTransformar(NodoIdentificador("hb"), NodoValor("rotar"), [NodoValor(90)]),
        NodoGraficar(NodoIdentificador("hb")),
    ]


@pytest.mark.parametrize(
    "transpilador, fragmentos",
    [
        (TranspiladorPython, ["from corelibs import *", "from standard_library import *", "def cobra_proyectar("]),
        (TranspiladorJavaScript, ["import * as io from './nativos/io.js';", "function cobra_proyectar(hb, modo) {"]),
        (TranspiladorRust, ["use crate::corelibs::*;", "use crate::standard_library::*;", "fn cobra_proyectar(hb: &str, modo: &str) {"]),
        (TranspiladorWasm, [";; runtime import: corelibs", ";; runtime import: standard_library", "(func $cobra_proyectar (param $hb i32) (param $modo i32)"]),
        (TranspiladorGo, ['"cobra/corelibs"', '"cobra/standard_library"', "func cobraProyectar(hb any, modo any) {"]),
        (TranspiladorCPP, ["#include <cobra/corelibs.hpp>", "#include <cobra/standard_library.hpp>", "inline void cobra_proyectar(const auto& hb, const auto& modo) {"]),
        (TranspiladorJava, ["import cobra.corelibs.*;", "import cobra.standard_library.*;", "private static void cobraProyectar(Object hb, Object modo) {"]),
        (TranspiladorASM, ["; runtime import corelibs", "; runtime import standard_library", "cobra_proyectar:"]),
    ],
)
def test_smoke_runtime_holobit_incluye_imports_y_hooks_validos(transpilador, fragmentos, ast_holobit_runtime):
    code = transpilador().generate_code(ast_holobit_runtime)
    for fragmento in fragmentos:
        assert fragmento in code


def test_module_map_resuelve_targets_en_cobra_toml_y_cobra_mod(tmp_path, monkeypatch):
    modulo = "biblioteca.co"
    toml_file = tmp_path / "cobra.toml"
    toml_file.write_text(
        "[modulos]\n"
        "[modulos.'biblioteca.co']\n"
        "python = 'biblioteca.py'\n"
        "js = 'biblioteca.js'\n",
        encoding="utf-8",
    )
    mod_file = tmp_path / "cobra.mod"
    mod_file.write_text(
        "[modulos]\n"
        "[modulos.'biblioteca.co']\n"
        "rust = 'biblioteca.rs'\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("COBRA_TOML", str(toml_file))
    monkeypatch.setenv("COBRA_MODULE_MAP", str(mod_file))

    import pcobra.cobra.transpilers.module_map as module_map

    module_map.COBRA_TOML_PATH = str(toml_file)
    module_map.MODULE_MAP_PATH = str(mod_file)
    module_map._toml_cache = None
    module_map._cache = None

    assert module_map.get_mapped_path(modulo, "python") == "biblioteca.py"
    assert module_map.get_mapped_path(modulo, "js") == "biblioteca.js"
    assert module_map.get_mapped_path(modulo, "rust") == "biblioteca.rs"
