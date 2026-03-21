import ast
from pathlib import Path

from pcobra.cobra.cli.commands.bench_cmd import BACKENDS as BENCH_BACKENDS
from pcobra.cobra.cli.commands.benchmarks_cmd import BACKENDS as BENCHMARKS_BACKENDS
from pcobra.cobra.cli.commands.compile_cmd import LANG_CHOICES
from pcobra.cobra.cli.commands.transpilar_inverso_cmd import EXTENSIONES_POR_LENGUAJE
from pcobra.cobra.transpilers.common.utils import STANDARD_IMPORTS
from pcobra.cobra.transpilers.feature_inspector import TRANSPILERS as FEATURE_INSPECTOR_TRANSPILERS
from pcobra.cobra.transpilers.registry import TRANSPILER_CLASS_PATHS
from pcobra.cobra.transpilers.reverse.policy import (
    REVERSE_SCOPE_LANGUAGES,
    normalize_reverse_language,
)
from pcobra.cobra.cli.target_policies import DOCKER_EXECUTABLE_TARGETS, TRANSPILATION_ONLY_TARGETS
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS


def _extract_backend_from_filename(path: Path, prefix: str = "to_") -> str:
    return path.stem.removeprefix(prefix)


def _canonical_reverse_impl_name(language: str) -> str:
    canonico = normalize_reverse_language(language)
    return "javascript" if canonico == "js" else canonico


def test_cli_y_transpilers_no_exponen_targets_fuera_de_whitelist_oficial():
    oficiales = set(OFFICIAL_TARGETS)

    assert tuple(LANG_CHOICES) == OFFICIAL_TARGETS
    assert tuple(TRANSPILER_CLASS_PATHS) == OFFICIAL_TARGETS
    assert set(STANDARD_IMPORTS.keys()).issubset(oficiales)
    assert set(BENCH_BACKENDS.keys()).issubset(oficiales)
    assert set(BENCHMARKS_BACKENDS.keys()).issubset(oficiales)
    assert set(FEATURE_INSPECTOR_TRANSPILERS.keys()).issubset(oficiales)
    assert "js" not in LANG_CHOICES
    assert "js" not in TRANSPILER_CLASS_PATHS
    assert "js" not in STANDARD_IMPORTS
    assert "js" not in BENCH_BACKENDS
    assert "js" not in BENCHMARKS_BACKENDS
    assert "js" not in FEATURE_INSPECTOR_TRANSPILERS


def test_mapa_reverse_extensions_esta_alineado_con_scope_reverse():
    reverse_scope = set(REVERSE_SCOPE_LANGUAGES)
    extension_keys = set(EXTENSIONES_POR_LENGUAJE.keys())

    assert reverse_scope.issubset(extension_keys)
    assert "javascript" in extension_keys
    assert "js" not in extension_keys


def test_archivos_to_py_en_transpiler_oficiales():
    base = Path("src/pcobra/cobra/transpilers/transpiler")
    found = {
        _extract_backend_from_filename(path)
        for path in base.glob("to_*.py")
        if path.name != "to_js.py"
    }
    if (base / "to_js.py").exists():
        found.add("javascript")

    oficiales = set(OFFICIAL_TARGETS)
    fuera_de_scope = sorted(found - oficiales)
    assert not fuera_de_scope, (
        "Se encontraron transpilers fuera de los 8 targets oficiales: "
        f"{', '.join(fuera_de_scope)}. "
        f"Oficiales: {', '.join(OFFICIAL_TARGETS)}"
    )


def test_archivos_reverse_from_py_en_scope_reverse():
    base = Path("src/pcobra/cobra/transpilers/reverse")
    found = {
        _extract_backend_from_filename(path, prefix="from_")
        for path in base.glob("from_*.py")
        if path.name != "from_js.py"
    }
    if (base / "from_js.py").exists():
        found.add("javascript")

    reverse_scope = set(REVERSE_SCOPE_LANGUAGES)
    fuera_de_scope = sorted(found - reverse_scope)
    assert not fuera_de_scope, (
        "Se encontraron reverse transpilers fuera del alcance definido en policy.py: "
        f"{', '.join(fuera_de_scope)}. "
        f"Permitidos reverse: {', '.join(REVERSE_SCOPE_LANGUAGES)}"
    )


def test_repo_no_contiene_to_o_from_py_fuera_de_las_rutas_oficiales():
    transpiler_dir = Path("src/pcobra/cobra/transpilers/transpiler")
    reverse_dir = Path("src/pcobra/cobra/transpilers/reverse")
    to_permitidos = {f"to_{target}.py" for target in OFFICIAL_TARGETS if target != "javascript"}
    to_permitidos.add("to_js.py")
    from_permitidos = {
        f"from_{target}.py" for target in REVERSE_SCOPE_LANGUAGES if target != "javascript"
    }
    from_permitidos.add("from_js.py")

    encontrados = []
    for path in Path(".").rglob("to_*.py"):
        if "__pycache__" in path.parts:
            continue
        if path.parent != transpiler_dir or path.name not in to_permitidos:
            encontrados.append(path.as_posix())
    for path in Path(".").rglob("from_*.py"):
        if "__pycache__" in path.parts:
            continue
        if path.parent != reverse_dir or path.name not in from_permitidos:
            encontrados.append(path.as_posix())

    assert not encontrados, (
        "Aparecieron módulos to_/from_ fuera del alcance o de las ubicaciones oficiales: "
        f"{encontrados}"
    )


def test_los_tests_no_importan_reverse_transpilers_fuera_del_scope_oficial():
    permitidos = set(REVERSE_SCOPE_LANGUAGES)
    encontrados_fuera_de_scope = {}

    for path in Path("tests").rglob("test_*.py"):
        modulo = ast.parse(path.read_text(encoding="utf-8"))
        imports_fuera_de_scope = set()

        for node in ast.walk(modulo):
            nombres = []
            if isinstance(node, ast.ImportFrom) and node.module:
                nombres = [node.module]
            elif isinstance(node, ast.Import):
                nombres = [alias.name for alias in node.names]

            for nombre in nombres:
                prefijo = None
                if nombre.startswith("cobra.transpilers.reverse.from_"):
                    prefijo = "cobra.transpilers.reverse.from_"
                elif nombre.startswith("pcobra.cobra.transpilers.reverse.from_"):
                    prefijo = "pcobra.cobra.transpilers.reverse.from_"

                if prefijo is None:
                    continue

                lenguaje = nombre.removeprefix(prefijo)
                canonico = _canonical_reverse_impl_name(lenguaje)
                if canonico not in permitidos:
                    imports_fuera_de_scope.add(lenguaje)

        if imports_fuera_de_scope:
            encontrados_fuera_de_scope[path.as_posix()] = sorted(imports_fuera_de_scope)

    assert not encontrados_fuera_de_scope, (
        "Se encontraron tests que importan reverse transpilers fuera del scope oficial: "
        f"{encontrados_fuera_de_scope}. Permitidos: {', '.join(REVERSE_SCOPE_LANGUAGES)}"
    )


def test_helpers_y_registros_de_tests_no_reintroducen_alias_js_como_nombre_publico():
    runtime_helper = Path("tests/utils/runtime.py").read_text(encoding="utf-8")
    transpile_time = Path("tests/performance/test_transpile_time.py").read_text(encoding="utf-8")

    assert '"js": _run_js' not in runtime_helper
    assert '{"python", "javascript", "js"}' not in runtime_helper
    assert '"js": "TranspiladorJavaScript"' not in transpile_time
    assert '"javascript": "TranspiladorJavaScript"' in transpile_time
    assert '"javascript": "js"' in transpile_time
    assert '_MODULE_SUFFIX_BY_TARGET' in transpile_time


def test_politicas_y_registros_publicos_no_aceptan_alias_js_como_target_feliz():
    assert "js" not in LANG_CHOICES
    assert "js" not in DOCKER_EXECUTABLE_TARGETS
    assert "js" not in OFFICIAL_TARGETS
    assert "js" not in REVERSE_SCOPE_LANGUAGES
    assert "js" not in TRANSPILER_CLASS_PATHS
    assert "js" not in FEATURE_INSPECTOR_TRANSPILERS
    assert "js" not in EXTENSIONES_POR_LENGUAJE


def test_politica_runtime_vs_transpilacion_es_explicita():
    assert set(DOCKER_EXECUTABLE_TARGETS).issubset(set(OFFICIAL_TARGETS))
    assert set(TRANSPILATION_ONLY_TARGETS) == {"wasm", "go", "java", "asm"}
    assert set(DOCKER_EXECUTABLE_TARGETS) | set(TRANSPILATION_ONLY_TARGETS) == set(OFFICIAL_TARGETS)


def test_validacion_ci_bloquea_condicionales_o_tablas_para_backend_c_fuera_de_zonas_historicas():
    from scripts.ci.validate_targets import validate_scan_roots

    errores = validate_scan_roots(tuple(OFFICIAL_TARGETS), tuple(REVERSE_SCOPE_LANGUAGES))
    errores_c = [error for error in errores if "backend retirado 'c'" in error]

    assert not errores_c, (
        "La auditoría CI detectó referencias no permitidas al backend retirado 'c': "
        f"{errores_c}"
    )
