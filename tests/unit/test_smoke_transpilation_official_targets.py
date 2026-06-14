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
from pcobra.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
from pcobra.cobra.transpilers.transpiler.to_rust import TranspiladorRust


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
        (TranspiladorPython, ["import pcobra.corelibs as _pcobra_corelibs", "import pcobra.standard_library as _pcobra_standard_library", "def cobra_holobit(", "def cobra_proyectar(", "def cobra_transformar(", "def cobra_graficar("]),
        (TranspiladorJavaScript, ["import * as io from './nativos/io.js';", "import * as interfaz from './nativos/interfaz.js';", "function cobra_holobit(valores)", "function cobra_proyectar(hb, modo)", "function cobra_transformar(hb, op", "function cobra_graficar(hb)"]),
        (TranspiladorRust, ["use crate::corelibs::*;", "use crate::standard_library::*;", "fn longitud<T: ToString>(valor: T) -> usize {", "fn cobra_holobit(", "fn cobra_proyectar(", "fn cobra_transformar(", "fn cobra_graficar("]),
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
    ],
)
def test_corelibs_y_standard_library_se_mantienen_sin_holobit(transpilador, fragmentos):
    code = transpilador().generate_code([NodoAsignacion(variable="x", expresion=NodoValor(1))])
    for fragmento in fragmentos:
        assert fragmento in code



def test_module_map_resuelve_targets_publicos_solo_desde_cobra_toml(tmp_path, monkeypatch):
    modulo = "biblioteca.co"
    toml_file = tmp_path / "cobra.toml"
    toml_file.write_text(
        "[modulos]\n"
        "[modulos.'biblioteca.co']\n"
        "python = 'biblioteca.py'\n"
        "javascript = 'biblioteca.js'\n"
        "rust = 'biblioteca.rs'\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("COBRA_TOML", str(toml_file))

    import pcobra.cobra.transpilers.module_map as module_map

    module_map.COBRA_TOML_PATH = str(toml_file)
    module_map._toml_cache = None

    assert module_map.get_mapped_path(modulo, "python") == "biblioteca.py"
    assert module_map.get_mapped_path(modulo, "javascript") == "biblioteca.js"
    assert module_map.get_mapped_path(modulo, "rust") == "biblioteca.rs"


def test_module_map_falla_si_toml_declara_target_no_publico(tmp_path, monkeypatch):
    toml_file = tmp_path / "cobra.toml"
    toml_file.write_text(
        "[modulos]\n"
        "[modulos.'biblioteca.co']\n"
        "go = 'biblioteca.go'\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("COBRA_TOML", str(toml_file))

    import pcobra.cobra.transpilers.module_map as module_map

    module_map.COBRA_TOML_PATH = str(toml_file)
    module_map._toml_cache = None

    with pytest.raises(ValueError, match="PUBLIC_BACKENDS"):
        module_map.get_toml_map()
