from pathlib import Path

from pcobra.cobra.cli.commands.bench_cmd import BACKENDS as BENCH_BACKENDS
from pcobra.cobra.cli.commands.benchmarks_cmd import BACKENDS as BENCHMARKS_BACKENDS
from pcobra.cobra.cli.commands.compile_cmd import LANG_CHOICES, TRANSPILERS
from pcobra.cobra.cli.commands.transpilar_inverso_cmd import EXTENSIONES_POR_LENGUAJE
from pcobra.cobra.cli.target_policies import (
    ADVANCED_HOLOBIT_RUNTIME_TARGETS,
    BEST_EFFORT_RUNTIME_TARGETS,
    DOCKER_EXECUTABLE_TARGETS,
    NO_RUNTIME_TARGETS,
    OFFICIAL_RUNTIME_TARGETS,
    OFFICIAL_STANDARD_LIBRARY_TARGETS,
    SDK_COMPATIBLE_TARGETS,
    TRANSPILATION_ONLY_TARGETS,
    VERIFICATION_EXECUTABLE_TARGETS,
    validate_runtime_support_contract,
)
from pcobra.cobra.transpilers.common.utils import STANDARD_IMPORTS
from pcobra.cobra.transpilers.feature_inspector import TRANSPILERS as FEATURE_INSPECTOR_TRANSPILERS
from pcobra.cobra.transpilers.registry import TRANSPILER_CLASS_PATHS, official_transpiler_targets
from pcobra.cobra.transpilers.reverse import REVERSE_SCOPE_LANGUAGES
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, TIER1_TARGETS, TIER2_TARGETS
from scripts.ci.validate_targets import (
    ALLOWED_HISTORICAL_PATH_PREFIXES,
    EXPECTED_GOLDEN_FILES,
    EXPECTED_TRANSPILER_MODULES,
    EXPECTED_TRANSPILER_REGISTRY,
    FINAL_OFFICIAL_TARGETS,
    validate_final_backend_repo_audit,
    validate_public_documentation_alignment,
    validate_python_policy_literals,
    validate_registry_tables,
    validate_scan_roots,
    validate_targeted_artifact_roots,
)
from scripts.targets_policy_common import VALIDATION_SCAN_PATHS, read_target_policy
from tests.utils.targets import assert_official_targets_partition



def test_fuente_canonica_y_registros_comparten_los_8_backends_oficiales():
    oficiales = tuple(OFFICIAL_TARGETS)
    particion = assert_official_targets_partition(transpilers=TRANSPILERS)

    assert len(oficiales) == 8
    assert oficiales == FINAL_OFFICIAL_TARGETS
    assert particion["tier1"] == TIER1_TARGETS
    assert particion["tier2"] == TIER2_TARGETS
    assert oficiales == TIER1_TARGETS + TIER2_TARGETS
    assert tuple(official_transpiler_targets()) == oficiales
    assert tuple(TRANSPILER_CLASS_PATHS) == oficiales
    assert tuple(TRANSPILERS) == oficiales
    assert tuple(LANG_CHOICES) == oficiales
    assert tuple(BENCHMARKS_BACKENDS) == oficiales
    assert set(BENCH_BACKENDS).issubset(oficiales)
    assert set(STANDARD_IMPORTS).issubset(oficiales)
    assert set(FEATURE_INSPECTOR_TRANSPILERS).issubset(oficiales)



def test_politica_publica_y_runtime_siguen_alineados_con_la_fuente_canonica():
    policy = read_target_policy()

    assert tuple(policy["tier1_targets"]) == TIER1_TARGETS
    assert tuple(policy["tier2_targets"]) == TIER2_TARGETS
    assert tuple(policy["official_targets"]) == OFFICIAL_TARGETS
    assert tuple(policy["official_runtime_targets"]) == OFFICIAL_RUNTIME_TARGETS
    assert tuple(policy["verification_targets"]) == VERIFICATION_EXECUTABLE_TARGETS
    assert tuple(policy["transpilation_only_targets"]) == TRANSPILATION_ONLY_TARGETS
    assert tuple(policy["best_effort_runtime_targets"]) == BEST_EFFORT_RUNTIME_TARGETS
    assert tuple(policy["no_runtime_targets"]) == NO_RUNTIME_TARGETS
    assert tuple(policy["official_standard_library_targets"]) == OFFICIAL_STANDARD_LIBRARY_TARGETS
    assert tuple(policy["advanced_holobit_runtime_targets"]) == ADVANCED_HOLOBIT_RUNTIME_TARGETS
    assert tuple(policy["sdk_compatible_targets"]) == SDK_COMPATIBLE_TARGETS



def test_runtime_contractual_permanece_consistente():
    validate_runtime_support_contract()

    assert OFFICIAL_RUNTIME_TARGETS == DOCKER_EXECUTABLE_TARGETS
    assert OFFICIAL_STANDARD_LIBRARY_TARGETS == OFFICIAL_RUNTIME_TARGETS
    assert ADVANCED_HOLOBIT_RUNTIME_TARGETS == OFFICIAL_RUNTIME_TARGETS
    assert set(OFFICIAL_RUNTIME_TARGETS).isdisjoint(BEST_EFFORT_RUNTIME_TARGETS)
    assert set(OFFICIAL_RUNTIME_TARGETS).isdisjoint(TRANSPILATION_ONLY_TARGETS)
    assert set(BEST_EFFORT_RUNTIME_TARGETS).isdisjoint(TRANSPILATION_ONLY_TARGETS)
    assert (
        set(OFFICIAL_RUNTIME_TARGETS)
        | set(BEST_EFFORT_RUNTIME_TARGETS)
        | set(TRANSPILATION_ONLY_TARGETS)
    ) == set(OFFICIAL_TARGETS)
    assert set(NO_RUNTIME_TARGETS) == set(TRANSPILATION_ONLY_TARGETS)
    assert SDK_COMPATIBLE_TARGETS == ("python",)



def test_reverse_scope_permanece_separado_pero_canonico():
    assert tuple(REVERSE_SCOPE_LANGUAGES) == ("python", "javascript", "java")
    assert set(REVERSE_SCOPE_LANGUAGES).issubset(OFFICIAL_TARGETS)
    assert set(REVERSE_SCOPE_LANGUAGES).issubset(EXTENSIONES_POR_LENGUAJE)



def test_modulos_y_artefactos_vigilados_cubren_solo_el_contrato_final():
    assert not validate_registry_tables()
    assert not validate_targeted_artifact_roots(tuple(OFFICIAL_TARGETS), tuple(REVERSE_SCOPE_LANGUAGES))



def test_auditoria_textual_y_documental_no_detecta_desalineaciones_publicas():
    assert not validate_scan_roots(tuple(OFFICIAL_TARGETS), tuple(REVERSE_SCOPE_LANGUAGES))
    assert not validate_public_documentation_alignment(
        tuple(OFFICIAL_TARGETS), tuple(REVERSE_SCOPE_LANGUAGES)
    )
    assert not validate_python_policy_literals(tuple(OFFICIAL_TARGETS))
    assert not validate_final_backend_repo_audit()



def test_rutas_bajo_vigilancia_siguen_incluyendo_docs_y_tests_relevantes():
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



def test_allowlist_historica_queda_limitada_a_rutas_archivadas():
    assert ALLOWED_HISTORICAL_PATH_PREFIXES == (
        "docs/historico/",
        "docs/experimental/",
        "archive/retired_targets/",
    )



def test_contrato_ci_fija_rutas_exactas_de_transpilers_y_goldens():
    assert EXPECTED_TRANSPILER_MODULES == (
        "src/pcobra/cobra/transpilers/transpiler/to_python.py",
        "src/pcobra/cobra/transpilers/transpiler/to_rust.py",
        "src/pcobra/cobra/transpilers/transpiler/to_js.py",
        "src/pcobra/cobra/transpilers/transpiler/to_wasm.py",
        "src/pcobra/cobra/transpilers/transpiler/to_go.py",
        "src/pcobra/cobra/transpilers/transpiler/to_cpp.py",
        "src/pcobra/cobra/transpilers/transpiler/to_java.py",
        "src/pcobra/cobra/transpilers/transpiler/to_asm.py",
    )
    assert EXPECTED_GOLDEN_FILES == (
        "tests/integration/transpilers/golden/python.golden",
        "tests/integration/transpilers/golden/rust.golden",
        "tests/integration/transpilers/golden/javascript.golden",
        "tests/integration/transpilers/golden/wasm.golden",
        "tests/integration/transpilers/golden/go.golden",
        "tests/integration/transpilers/golden/cpp.golden",
        "tests/integration/transpilers/golden/java.golden",
        "tests/integration/transpilers/golden/asm.golden",
    )
    assert EXPECTED_TRANSPILER_REGISTRY == {
        "python": ("pcobra.cobra.transpilers.transpiler.to_python", "TranspiladorPython"),
        "rust": ("pcobra.cobra.transpilers.transpiler.to_rust", "TranspiladorRust"),
        "javascript": ("pcobra.cobra.transpilers.transpiler.to_js", "TranspiladorJavaScript"),
        "wasm": ("pcobra.cobra.transpilers.transpiler.to_wasm", "TranspiladorWasm"),
        "go": ("pcobra.cobra.transpilers.transpiler.to_go", "TranspiladorGo"),
        "cpp": ("pcobra.cobra.transpilers.transpiler.to_cpp", "TranspiladorCPP"),
        "java": ("pcobra.cobra.transpilers.transpiler.to_java", "TranspiladorJava"),
        "asm": ("pcobra.cobra.transpilers.transpiler.to_asm", "TranspiladorASM"),
    }
