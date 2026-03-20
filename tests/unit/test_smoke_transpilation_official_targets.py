import pytest

from pcobra.core.ast_nodes import (
    NodoAsignacion,
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
        (TranspiladorPython, ["from corelibs import *", "from standard_library import *", "def cobra_holobit(", "def cobra_proyectar(", "def cobra_transformar(", "def cobra_graficar("]),
        (TranspiladorJavaScript, ["import * as io from './nativos/io.js';", "function cobra_holobit(valores)", "function cobra_proyectar(hb, modo)", "function cobra_transformar(hb, op", "function cobra_graficar(hb)"]),
        (TranspiladorRust, ["use crate::corelibs::*;", "use crate::standard_library::*;", "fn cobra_holobit(", "fn cobra_proyectar(", "fn cobra_transformar(", "fn cobra_graficar("]),
        (TranspiladorWasm, ["(func $cobra_holobit", "(func $cobra_proyectar", "(func $cobra_transformar", "(func $cobra_graficar", "runtime administrados externamente"]),
        (TranspiladorGo, ['"cobra/corelibs"', '"cobra/standard_library"', "func cobra_holobit(", "func cobra_proyectar(", "func cobra_transformar(", "func cobra_graficar("]),
        (TranspiladorCPP, ["#include <cobra/corelibs.hpp>", "#include <cobra/standard_library.hpp>", "inline auto cobra_holobit", "inline void cobra_proyectar", "inline void cobra_transformar", "inline void cobra_graficar"]),
        (TranspiladorJava, ["import cobra.corelibs.*;", "import cobra.standard_library.*;", "private static Object cobra_holobit", "private static void cobra_proyectar", "private static void cobra_transformar", "private static void cobra_graficar"]),
        (TranspiladorASM, ["cobra_holobit:", "cobra_proyectar:", "cobra_transformar:", "cobra_graficar:", "TRAP"]),
    ],
)
def test_smoke_runtime_holobit_incluye_imports_y_hooks_validos(transpilador, fragmentos, ast_holobit_runtime):
    code = transpilador().generate_code(ast_holobit_runtime)
    for fragmento in fragmentos:
        assert fragmento in code


@pytest.mark.parametrize(
    "transpilador, fragmentos",
    [
        (TranspiladorPython, ["corelibs", "standard_library"]),
        (TranspiladorRust, ["corelibs", "standard_library"]),
        (TranspiladorWasm, ["runtime administrados externamente"]),
        (TranspiladorGo, ["cobra/corelibs", "cobra/standard_library"]),
        (TranspiladorCPP, ["cobra/corelibs.hpp", "cobra/standard_library.hpp"]),
        (TranspiladorJava, ["cobra.corelibs", "cobra.standard_library"]),
    ],
)
def test_corelibs_y_standard_library_se_mantienen_sin_holobit(transpilador, fragmentos):
    code = transpilador().generate_code([NodoAsignacion(variable="x", expresion=NodoValor(1))])
    for fragmento in fragmentos:
        assert fragmento in code


def test_smoke_runtime_holobit_asm_expone_fallo_explicito_y_homogeneo(ast_holobit_runtime):
    code = TranspiladorASM().generate_code(ast_holobit_runtime)
    assert "Runtime Holobit ASM: 'proyectar' requiere runtime avanzado compatible." in code
    assert "Runtime Holobit ASM: 'transformar' requiere runtime avanzado compatible." in code
    assert "Runtime Holobit ASM: 'graficar' requiere runtime avanzado compatible." in code


def test_module_map_resuelve_targets_en_cobra_toml_y_cobra_mod(tmp_path, monkeypatch):
    modulo = "biblioteca.co"
    toml_file = tmp_path / "cobra.toml"
    toml_file.write_text(
        "[modulos]\n"
        "[modulos.'biblioteca.co']\n"
        "python = 'biblioteca.py'\n"
        "javascript = 'biblioteca.js'\n",
        encoding="utf-8",
    )
    mod_file = tmp_path / "cobra.mod"
    mod_file.write_text(
        "[modulos]\n"
        "[modulos.'biblioteca.co']\n"
        "rust = 'biblioteca.rs'\n"
        "go = 'biblioteca.go'\n",
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
    assert module_map.get_mapped_path(modulo, "javascript") == "biblioteca.js"
    assert module_map.get_mapped_path(modulo, "rust") == "biblioteca.rs"
    assert module_map.get_mapped_path(modulo, "go") == "biblioteca.go"
