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
from pcobra.cobra.cli.target_policies import (
    BEST_EFFORT_RUNTIME_TARGETS,
    DOCKER_EXECUTABLE_TARGETS,
    NO_RUNTIME_TARGETS,
    OFFICIAL_RUNTIME_TARGETS,
    TRANSPILATION_ONLY_TARGETS,
    VERIFICATION_EXECUTABLE_TARGETS,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, TIER1_TARGETS, TIER2_TARGETS
from scripts.targets_policy_common import (
    HOLOBIT_MATRIX_DOC_PATHS,
    PUBLIC_RUNTIME_POLICY_PATHS,
    VALIDATION_SCAN_PATHS,
    read_target_policy,
)


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
    assert tuple(BENCHMARKS_BACKENDS) == OFFICIAL_TARGETS
    assert set(FEATURE_INSPECTOR_TRANSPILERS.keys()).issubset(oficiales)
    assert "js" not in LANG_CHOICES
    assert "js" not in TRANSPILER_CLASS_PATHS
    assert "js" not in STANDARD_IMPORTS
    assert "js" not in BENCH_BACKENDS
    assert "js" not in BENCHMARKS_BACKENDS
    assert "js" not in FEATURE_INSPECTOR_TRANSPILERS




def test_targets_y_tiers_oficiales_permancen_exactos():
    policy = read_target_policy()

    assert tuple(policy["tier1_targets"]) == TIER1_TARGETS
    assert tuple(policy["tier2_targets"]) == TIER2_TARGETS
    assert tuple(policy["official_targets"]) == OFFICIAL_TARGETS
    assert TIER1_TARGETS + TIER2_TARGETS == OFFICIAL_TARGETS

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

    assert found == set(OFFICIAL_TARGETS), (
        "Los módulos to_*.py deben corresponder exactamente a los 8 targets oficiales: "
        f"encontrados={sorted(found)}, oficiales={list(OFFICIAL_TARGETS)}"
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
    policy = read_target_policy()

    assert tuple(policy["official_runtime_targets"]) == OFFICIAL_RUNTIME_TARGETS
    assert OFFICIAL_RUNTIME_TARGETS == DOCKER_EXECUTABLE_TARGETS
    assert tuple(policy["transpilation_only_targets"]) == TRANSPILATION_ONLY_TARGETS
    assert tuple(policy["verification_targets"]) == VERIFICATION_EXECUTABLE_TARGETS
    assert set(DOCKER_EXECUTABLE_TARGETS) | set(TRANSPILATION_ONLY_TARGETS) == set(OFFICIAL_TARGETS)


def test_politica_best_effort_experimental_queda_acotada_y_explicita():
    assert BEST_EFFORT_RUNTIME_TARGETS == ("go", "java")
    assert NO_RUNTIME_TARGETS == ("wasm", "asm")
    assert set(BEST_EFFORT_RUNTIME_TARGETS) | set(NO_RUNTIME_TARGETS) == set(TRANSPILATION_ONLY_TARGETS)


def test_validacion_ci_bloquea_condicionales_o_tablas_para_backend_c_fuera_de_zonas_historicas():
    from scripts.ci.validate_targets import validate_scan_roots

    errores = validate_scan_roots(tuple(OFFICIAL_TARGETS), tuple(REVERSE_SCOPE_LANGUAGES))
    errores_c = [error for error in errores if "backend retirado 'c'" in error]

    assert not errores_c, (
        "La auditoría CI detectó referencias no permitidas al backend retirado 'c': "
        f"{errores_c}"
    )


def test_rutas_bajo_vigilancia_incluyen_docs_y_tests_pedidos():
    root = Path.cwd().resolve()
    rel_paths = {path.resolve().relative_to(root).as_posix() for path in VALIDATION_SCAN_PATHS}

    assert "README.md" in rel_paths
    assert "docs" in rel_paths
    assert "docs/MANUAL_COBRA.md" in rel_paths
    assert "examples" in rel_paths
    assert "docker" in rel_paths
    assert "extensions" in rel_paths
    assert "tests/utils" in rel_paths
    assert "tests/performance" in rel_paths
    assert "tests/integration" in rel_paths


def test_allowlist_historica_queda_limitada_a_docs_archivados():
    from scripts.ci.validate_targets import ALLOWED_HISTORICAL_PATH_PREFIXES

    assert ALLOWED_HISTORICAL_PATH_PREFIXES == (
        "docs/historico/",
        "docs/experimental/",
    )


def test_validacion_ci_verifica_listas_publicas_de_runtime_y_matrices_holobit():
    from scripts.ci.validate_targets import (
        validate_holobit_public_contract,
        validate_public_policy_lists,
    )

    policy = read_target_policy()
    errores_listas = validate_public_policy_lists(
        tuple(policy["official_targets"]),
        tuple(REVERSE_SCOPE_LANGUAGES),
        official_runtime_targets=tuple(policy["official_runtime_targets"]),
        transpilation_only_targets=tuple(policy["transpilation_only_targets"]),
        verification_targets=tuple(policy["verification_targets"]),
    )
    errores_holobit = validate_holobit_public_contract()

    assert tuple(path.as_posix() for path in PUBLIC_RUNTIME_POLICY_PATHS)
    assert tuple(path.as_posix() for path in HOLOBIT_MATRIX_DOC_PATHS)
    assert not errores_listas, f"Listas públicas desalineadas: {errores_listas}"
    assert not errores_holobit, f"Claims/matriz Holobit desalineados: {errores_holobit}"


def test_validacion_ci_bloquea_flags_publicos_obsoletos_en_docs_y_examples():
    from scripts.ci.validate_targets import validate_scan_roots

    errores = validate_scan_roots(tuple(OFFICIAL_TARGETS), tuple(REVERSE_SCOPE_LANGUAGES))
    errores_flags = [
        error
        for error in errores
        if "opción CLI pública obsoleta/no canónica" in error
    ]

    assert not errores_flags, (
        "La auditoría CI detectó flags públicos obsoletos en documentación/ejemplos: "
        f"{errores_flags}"
    )


def test_tooling_y_fixtures_importan_targets_canonicos_sin_listas_locales_divergentes():
    from scripts.ci.validate_targets import validate_python_policy_literals

    policy = read_target_policy()
    errors = validate_python_policy_literals(
        tuple(policy["official_targets"]),
        official_runtime_targets=tuple(policy["official_runtime_targets"]),
        transpilation_only_targets=tuple(policy["transpilation_only_targets"]),
        best_effort_runtime_targets=tuple(policy["best_effort_runtime_targets"]),
        no_runtime_targets=tuple(policy["no_runtime_targets"]),
        verification_targets=tuple(policy["verification_targets"]),
    )

    assert not errors, (
        "Se detectaron listas hardcodeadas o desalineadas en tooling/tests vigilados: "
        f"{errors}"
    )
