"""Contratos de colección para preservar una única identidad canónica del AST."""

from __future__ import annotations

import ast
import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from pcobra.core import ast_nodes

ROOT = Path(__file__).resolve().parents[2]
NEW_IMPORT_CONTRACT_TESTS = (Path(__file__).resolve(),)
CANONICAL_MODULE_NAMES = (
    "pcobra.core.ast_nodes",
    "pcobra.core.interpreter",
    "pcobra.core.parser",
    "pcobra.cobra.core.ast_nodes",
    "pcobra.cobra.core.interpreter",
    "pcobra.cobra.core.parser",
    "pcobra.cobra.transpilers.transpiler.to_js",
    "pcobra.cobra.transpilers.transpiler.to_python",
    "pcobra.cobra.transpilers.transpiler.to_rust",
)
FORBIDDEN_IMPORT_SURFACES = ("core.ast_nodes", "cobra.core")
CANONICAL_MODULES = {
    name: importlib.import_module(name) for name in CANONICAL_MODULE_NAMES
}


def _run_clean_ast_identity_probe(
    first: str, second: str, *, phase: int = 2, enabled: bool = True
) -> subprocess.CompletedProcess:
    """Ejecuta la sonda con la ruta legacy primero y sin estado de pytest."""

    classes = (
        "NodoAST",
        "NodoClase",
        "NodoMetodo",
        "NodoAtributo",
        "NodoLlamadaFuncion",
        "NodoInstancia",
        "NodoLlamadaMetodo",
    )
    script = f"""
import importlib

first = importlib.import_module({first!r})
second = importlib.import_module({second!r})
canonical = importlib.import_module('pcobra.core.ast_nodes')
legacy = importlib.import_module('core.ast_nodes')

assert first is second
assert canonical is legacy
for name in {classes!r}:
    assert getattr(canonical, name) is getattr(legacy, name), name

legacy_node = legacy.NodoInstancia('Clase')
canonical_node = canonical.NodoLlamadaMetodo(
    canonical.NodoIdentificador('obj'), 'metodo', []
)
assert isinstance(legacy_node, canonical.NodoAST)
assert isinstance(canonical_node, legacy.NodoAST)

constant_folder = importlib.import_module(
    'pcobra.core.optimizations.constant_folder'
)
assert constant_folder.NodoAST is canonical.NodoAST
assert constant_folder.optimize_constants([legacy_node]) == [legacy_node]
"""
    env = os.environ.copy()
    env["PCOBRA_LEGACY_IMPORT_PHASE"] = str(phase)
    if enabled:
        env["PCOBRA_ENABLE_LEGACY_IMPORTS"] = "1"
    else:
        env.pop("PCOBRA_ENABLE_LEGACY_IMPORTS", None)
    # Reproduce la arquitectura histórica que exponía ``core`` directamente.
    env["PYTHONPATH"] = os.pathsep.join(
        (str(ROOT / "src" / "pcobra"), str(ROOT / "src"))
    )
    return subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT.parent,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_clases_ast_activas_proceden_del_modulo_canonico() -> None:
    canonical_class = ast_nodes.NodoAST

    assert canonical_class.__module__ == "pcobra.core.ast_nodes"
    for name, module in CANONICAL_MODULES.items():
        exported_class = getattr(module, "NodoAST", None)
        if exported_class is not None:
            assert exported_class is canonical_class, name
            assert exported_class.__module__ == "pcobra.core.ast_nodes", name


def test_modulos_oficiales_tienen_una_sola_clave_canonica() -> None:
    # Un proceso limpio evita que los contratos de compatibilidad legacy de
    # otros casos contaminen sys.modules y simulen una segunda carga oficial.
    script = f"""
import importlib
import pathlib
import sys

names = {CANONICAL_MODULE_NAMES!r}
modules = {{name: importlib.import_module(name) for name in names}}
for canonical_name, module in modules.items():
    module_path = pathlib.Path(module.__file__).resolve()
    names_for_same_file = {{
        name
        for name, loaded in sys.modules.items()
        if getattr(loaded, '__file__', None)
        and pathlib.Path(loaded.__file__).resolve() == module_path
    }}
    assert module.__name__ == canonical_name
    expected_names = {{canonical_name}}
    if canonical_name == 'pcobra.core.ast_nodes':
        expected_names.add('core.ast_nodes')
    assert names_for_same_file == expected_names, (canonical_name, names_for_same_file)
    assert canonical_name.startswith('pcobra.')
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_contrato_checkout_shim_ast_reutiliza_identidad_canonica_en_ambos_ordenes() -> (
    None
):
    """El shim del source tree conserva la identidad AST en ambos órdenes."""

    clases = ("NodoAST", "NodoValor", "NodoAsignacion", "NodoFuncion", "NodoUsar")
    ordenes = (
        ("pcobra.core.ast_nodes", "core.ast_nodes"),
        ("core.ast_nodes", "pcobra.core.ast_nodes"),
    )

    for primero, segundo in ordenes:
        script = f"""
import importlib
import importlib.util

if importlib.util.find_spec('core') is None:
    raise SystemExit('el shim histórico core no está disponible en este checkout')

primero = importlib.import_module({primero!r})
segundo = importlib.import_module({segundo!r})
canonical = importlib.import_module('pcobra.core.ast_nodes')
legacy = importlib.import_module('core.ast_nodes')

assert canonical is legacy, (canonical, legacy)
for nombre in {clases!r}:
    assert getattr(canonical, nombre) is getattr(legacy, nombre), nombre
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("phase", "opt_in", "legacy_enabled"),
    (
        (1, False, True),
        (2, True, True),
        (2, False, False),
        (3, False, False),
        (3, True, False),
    ),
)
def test_checkout_shim_respeta_politica_legacy(
    phase: int, opt_in: bool, legacy_enabled: bool
) -> None:
    """Prueba el shim físico desde la raíz con únicamente ``src`` en PYTHONPATH."""

    script = f"""
import importlib
import sys

if {legacy_enabled!r}:
    legacy = importlib.import_module('core.ast_nodes')
    canonical = importlib.import_module('pcobra.core.ast_nodes')
    import core
    import pcobra.core

    assert canonical.NodoAST.__module__ == 'pcobra.core.ast_nodes'
    assert legacy is canonical
    assert core.ast_nodes is pcobra.core.ast_nodes
    assert legacy.NodoAST is canonical.NodoAST

    constant_folder = importlib.import_module(
        'pcobra.core.optimizations.constant_folder'
    )
    node = canonical.NodoInstancia('Clase')
    assert constant_folder.NodoAST is canonical.NodoAST
    assert constant_folder.optimize_constants([node]) == [node]
else:
    try:
        importlib.import_module('core.ast_nodes')
    except ImportError as exc:
        assert 'Compatibilidad de imports legacy deshabilitada' in str(exc)
        assert 'pcobra.core' in str(exc)
    else:
        raise AssertionError('core.ast_nodes debía ser rechazado')

    assert not [name for name in sys.modules if name.startswith('core.')]
    canonical = importlib.import_module('pcobra.core.ast_nodes')
    assert canonical.NodoAST.__module__ == 'pcobra.core.ast_nodes'
    assert 'core.ast_nodes' not in sys.modules
"""
    env = os.environ.copy()
    env["PCOBRA_LEGACY_IMPORT_PHASE"] = str(phase)
    if opt_in:
        env["PCOBRA_ENABLE_LEGACY_IMPORTS"] = "1"
    else:
        env.pop("PCOBRA_ENABLE_LEGACY_IMPORTS", None)
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_ast_identity_core_then_pcobra_core() -> None:
    result = _run_clean_ast_identity_probe("core.ast_nodes", "pcobra.core.ast_nodes")

    assert result.returncode == 0, result.stderr


def test_ast_identity_pcobra_core_then_core() -> None:
    result = _run_clean_ast_identity_probe("pcobra.core.ast_nodes", "core.ast_nodes")

    assert result.returncode == 0, result.stderr


def test_ast_identity_fase_1_sin_opt_in_conserva_compatibilidad() -> None:
    result = _run_clean_ast_identity_probe(
        "core.ast_nodes", "pcobra.core.ast_nodes", phase=1, enabled=False
    )

    assert result.returncode == 0, result.stderr


def test_ast_legacy_primero_enlaza_el_hijo_con_el_paquete_canonico() -> None:
    """El alias en sys.modules también queda visible como atributo del padre."""

    script = """
import core.ast_nodes
import pcobra.core
import pcobra.core.ast_nodes

assert pcobra.core.ast_nodes is core.ast_nodes
assert pcobra.core.ast_nodes.NodoAST is core.ast_nodes.NodoAST
"""
    env = os.environ.copy()
    env["PCOBRA_LEGACY_IMPORT_PHASE"] = "2"
    env["PCOBRA_ENABLE_LEGACY_IMPORTS"] = "1"
    env["PYTHONPATH"] = os.pathsep.join(
        (str(ROOT / "src" / "pcobra"), str(ROOT / "src"))
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT.parent,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_ast_canonico_no_registra_alias_si_legacy_esta_deshabilitado() -> None:
    """El AST respeta la fase resuelta por la gobernanza de imports legacy."""

    script = """
import sys
import pcobra.core.ast_nodes

assert 'core.ast_nodes' not in sys.modules
"""
    env = os.environ.copy()
    env["PCOBRA_LEGACY_IMPORT_PHASE"] = "2"
    env.pop("PCOBRA_ENABLE_LEGACY_IMPORTS", None)
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("phase", "opt_in"),
    (
        (2, False),
        (3, False),
        (3, True),
    ),
)
def test_ast_legacy_se_rechaza_segun_politica_y_canonico_funciona(
    phase: int, opt_in: bool
) -> None:
    """La ruta física histórica no elude las fases que desactivan legacy."""

    script = """
import importlib
import sys

try:
    importlib.import_module('core.ast_nodes')
except ImportError as exc:
    assert 'Compatibilidad de imports legacy deshabilitada' in str(exc)
    assert 'pcobra.core.ast_nodes' in str(exc)
else:
    raise AssertionError('core.ast_nodes debía ser rechazado')

assert 'core.ast_nodes' not in sys.modules
canonical = importlib.import_module('pcobra.core.ast_nodes')
assert canonical.NodoAST.__module__ == 'pcobra.core.ast_nodes'
assert 'core.ast_nodes' not in sys.modules

constant_folder = importlib.import_module(
    'pcobra.core.optimizations.constant_folder'
)
node = canonical.NodoInstancia('Clase')
assert constant_folder.optimize_constants([node]) == [node]
"""
    env = os.environ.copy()
    env["PCOBRA_LEGACY_IMPORT_PHASE"] = str(phase)
    if opt_in:
        env["PCOBRA_ENABLE_LEGACY_IMPORTS"] = "1"
    else:
        env.pop("PCOBRA_ENABLE_LEGACY_IMPORTS", None)
    env["PYTHONPATH"] = os.pathsep.join(
        (str(ROOT / "src" / "pcobra"), str(ROOT / "src"))
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT.parent,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_pruebas_nuevas_no_importan_superficies_legacy() -> None:
    violations: list[str] = []

    for path in NEW_IMPORT_CONTRACT_TESTS:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names = (alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imported_names = (node.module,)
            else:
                continue

            for imported_name in imported_names:
                if any(
                    imported_name == surface or imported_name.startswith(f"{surface}.")
                    for surface in FORBIDDEN_IMPORT_SURFACES
                ):
                    violations.append(
                        f"{path.relative_to(ROOT)}:{node.lineno} -> {imported_name}"
                    )

    assert violations == []
