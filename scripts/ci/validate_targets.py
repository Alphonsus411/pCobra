#!/usr/bin/env python3
"""Validaciones CI estrictas para el contrato final de 8 backends."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pcobra.cobra.cli.commands.benchmarks_cmd import BACKENDS as BENCHMARKS_BACKENDS
from pcobra.cobra.cli.commands.compile_cmd import LANG_CHOICES, TRANSPILERS
from pcobra.cobra.cli.target_policies import SDK_COMPATIBLE_TARGETS
from pcobra.cobra.transpilers.compatibility_matrix import (
    BACKEND_COMPATIBILITY,
    BACKEND_FEATURE_GAPS,
    CONTRACT_FEATURES,
    SDK_FULL_BACKENDS,
    validate_backend_compatibility_contract,
)
from pcobra.cobra.transpilers.registry import (
    TRANSPILER_CLASS_PATHS,
    official_transpiler_module_filenames,
    official_transpiler_registry_literal,
    official_transpiler_targets,
)
from pcobra.cobra.transpilers.reverse import REVERSE_SCOPE_LANGUAGES
from pcobra.cobra.transpilers.targets import (
    OFFICIAL_TARGETS,
    TIER1_TARGETS,
    TIER2_TARGETS,
)
from scripts.targets_policy_common import (
    FORBIDDEN_PUBLIC_TARGET_ALIASES,
    HOLOBIT_MATRIX_DOC_PATHS,
    PUBLIC_RUNTIME_POLICY_PATHS,
    PUBLIC_TEXT_PATHS,
    find_non_python_sdk_promotion_errors,
    find_public_alias_errors,
    read_target_policy,
)

FINAL_OFFICIAL_TARGETS = tuple(OFFICIAL_TARGETS)
EXPECTED_TRANSPILER_MODULES = tuple(
    f"src/pcobra/cobra/transpilers/transpiler/{filename}"
    for filename in official_transpiler_module_filenames()
)
EXPECTED_GOLDEN_FILES = tuple(
    f"tests/integration/transpilers/golden/{target}.golden"
    for target in FINAL_OFFICIAL_TARGETS
)
EXPECTED_TRANSPILER_REGISTRY = official_transpiler_registry_literal()
CRITICAL_DOCS_GENERATED_CONTRACT = {
    "README.md": (
        "<!-- BEGIN GENERATED TARGET POLICY SUMMARY -->",
        "<!-- END GENERATED TARGET POLICY SUMMARY -->",
    ),
    "docs/frontend/backends.rst": (
        ".. include:: ../_generated/target_policy_summary.rst",
        ".. include:: ../_generated/cli_backend_examples.rst",
    ),
    "docs/frontend/cli.rst": (
        ".. include:: ../_generated/target_policy_summary.rst",
        ".. include:: ../_generated/cli_backend_examples.rst",
    ),
}

TRANSPILER_DIR = ROOT / "src/pcobra/cobra/transpilers/transpiler"
REVERSE_DIR = ROOT / "src/pcobra/cobra/transpilers/reverse"
GOLDEN_DIR = ROOT / "tests/integration/transpilers/golden"
TARGET_CHECKLIST_PATH = ROOT / "docs/issues/target_cleanup_checklist.md"
ALLOWED_HISTORICAL_PATH_PREFIXES = (
    "docs/historico/",
    "docs/experimental/",
    "archive/retired_targets/",
)
REPO_AUDIT_ALLOWED_PATH_PREFIXES = ALLOWED_HISTORICAL_PATH_PREFIXES
REPO_AUDIT_SCAN_ROOTS = ("src", "docs", "tests", "scripts")
REPO_AUDIT_ALLOWED_FILE_PATHS = frozenset(
    {
        "scripts/lint_legacy_aliases.py",
        "scripts/targets_policy_common.py",
        "scripts/validate_targets_policy.py",
        "scripts/ci/validate_targets.py",
        "tests/unit/test_cli_target_aliases.py",
        "tests/unit/test_public_docs_scope.py",
        "tests/unit/test_validate_targets_policy_script.py",
        "tests/unit/test_reverse_transpilers_registry.py",
        "tests/unit/test_verify_cmd.py",
        "tests/unit/test_cli_compilar_tipos.py",
        "tests/performance/test_transpile_time.py",
        "scripts/benchmarks/targets_policy.py",
        "docs/frontend/uml/arquitectura_general.puml",
    }
)
REPO_AUDIT_FORBIDDEN_TERMS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"(?<![\w/-])hololang(?![\w/-])", re.IGNORECASE),
        "backend retirado 'hololang'",
    ),
    (
        re.compile(r"(?<![\w/-])reverse[ -]wasm(?![\w/-])", re.IGNORECASE),
        "pipeline retirado 'reverse wasm'",
    ),
    (
        re.compile(r"(?<![\w/-])llvm(?![\w/-])", re.IGNORECASE),
        "backend/pipeline retirado 'llvm'",
    ),
    (
        re.compile(r"(?<![\w/-])latex(?![\w/-])", re.IGNORECASE),
        "backend/pipeline retirado 'latex'",
    ),
)
REPO_AUDIT_FORBIDDEN_ALIAS_LITERALS: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (
        re.compile(
            r'(?P<quote>["\'])' + re.escape(alias) + r"(?P=quote)", re.IGNORECASE
        ),
        alias,
    )
    for alias, _ in FORBIDDEN_PUBLIC_TARGET_ALIASES
)
DOC_TABLE_PATHS = (
    "docs/targets_policy.md",
    "docs/matriz_transpiladores.md",
    "docs/contrato_runtime_holobit.md",
)
RETIRED_TARGETS_LITERAL = "archive/retired_targets"
DOC_INDEX_GUARDRAIL_PATHS = (
    "README.md",
    "docs/README.en.md",
    "docs/frontend/index.rst",
    "docs/conf.py",
    "docs/frontend/conf.py",
)
PACKAGING_GUARDRAIL_PATHS = (
    "pyproject.toml",
    "MANIFEST.in",
)
IMPORT_GUARDRAIL_SCAN_ROOTS = ("src", "scripts", "tests")
IMPORT_GUARDRAIL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?m)^\s*from\s+archive(?:\.[\w_]+)*\s+import\s+"),
    re.compile(r"(?m)^\s*import\s+archive(?:\.[\w_]+)*"),
    re.compile(
        r"(?i)(sys\.path\.insert|sys\.path\.append|Path\()[^\n]{0,200}archive/retired_targets"
    ),
)
FORBIDDEN_NON_PYTHON_SDK_PROMOTION = re.compile(
    r"(?P<backend>javascript|rust|wasm|go|cpp|java|asm)[^\n]{0,120}"
    r"\b(figura como|aparece como|es|tiene)\b[^\n]{0,40}"
    r"(full|compatibilidad total con holobit sdk|compatibilidad sdk completa)",
    re.IGNORECASE,
)
CHECKLIST_BLOCKS: dict[str, str] = {
    "to_modules": "módulos to_*.py",
    "nodes_dirs": "directorios *_nodes",
    "golden_files": "golden files",
    "policy_cli": "políticas CLI",
    "policy_benchmark": "políticas benchmark",
    "policy_docker": "políticas docker",
    "policy_docs": "políticas docs",
    "canonical_cli_commands": "set canónico CLI",
}
PHASE_CHECKBOX_PATTERN = re.compile(r"^- \[(?P<mark>[ xX])\]\s+", re.MULTILINE)
PHASE_HEADER_PATTERN = re.compile(r"^###\s+Fase\s+\d+\s+—\s+.+$", re.MULTILINE)
CANONICAL_POLICY_CLI_COMMANDS: tuple[str, ...] = (
    "cobra compilar",
    "cobra verificar",
    "cobra benchmarks",
    "cobra transpilar-inverso",
)
CLI_POLICY_DOCS = (
    "docs/targets_policy.md",
    "docs/matriz_transpiladores.md",
    "docs/contrato_runtime_holobit.md",
    "docs/issues/target_cleanup_checklist.md",
)


def _ordered(items: set[str] | tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(target for target in FINAL_OFFICIAL_TARGETS if target in set(items))


def _extract_checklist_block(content: str, block_name: str) -> tuple[str, ...]:
    pattern = re.compile(
        rf"<!-- BEGIN {re.escape(block_name)} -->\n(?P<body>.*?)\n<!-- END {re.escape(block_name)} -->",
        re.DOTALL,
    )
    match = pattern.search(content)
    if not match:
        raise RuntimeError(
            f"{TARGET_CHECKLIST_PATH.relative_to(ROOT).as_posix()}: falta bloque '{block_name}'"
        )
    items = tuple(re.findall(r"^- `([^`]+)`", match.group("body"), flags=re.MULTILINE))
    if not items:
        raise RuntimeError(
            f"{TARGET_CHECKLIST_PATH.relative_to(ROOT).as_posix()}: bloque '{block_name}' sin elementos"
        )
    return items


def _markdown_table_rows(path: Path) -> list[tuple[int, list[str]]]:
    rows: list[tuple[int, list[str]]] = []
    for line_no, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        stripped = line.strip()
        if not stripped.startswith("| `"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        rows.append((line_no, cells))
    return rows


def _extract_doc_backend_rows(path: Path) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for line_no, cells in _markdown_table_rows(path):
        backend = cells[0].strip().strip("`")
        if backend:
            rows.append((line_no, backend))
    return rows


def _parse_backend_matrix_table(doc_path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for _line_no, cells in _markdown_table_rows(doc_path):
        if len(cells) < 8:
            continue
        backend = cells[0].strip("`")
        if len(cells) >= 10:
            feature_offset = 4
            tier = cells[2].lower().replace(" ", "")
        else:
            feature_offset = 2
            tier = cells[1].lower().replace(" ", "")
        rows[backend] = {
            "tier": tier,
            "holobit": cells[feature_offset].split()[-1],
            "proyectar": cells[feature_offset + 1].split()[-1],
            "transformar": cells[feature_offset + 2].split()[-1],
            "graficar": cells[feature_offset + 3].split()[-1],
            "corelibs": cells[feature_offset + 4].split()[-1],
            "standard_library": cells[feature_offset + 5].split()[-1],
        }
    return rows


def _extract_targets_policy_tier(path: Path, heading: str) -> tuple[str, ...]:
    content = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"### {re.escape(heading)}\n\n(?P<body>(?:- `[^`]+`\n)+)",
        re.MULTILINE,
    )
    match = pattern.search(content)
    if not match:
        raise RuntimeError(
            f"{path.relative_to(ROOT).as_posix()}: falta la sección '{heading}'"
        )
    return tuple(re.findall(r"`([^`]+)`", match.group("body")))


def _is_historical_repo_path(rel: str) -> bool:
    return rel in REPO_AUDIT_ALLOWED_FILE_PATHS or rel.startswith(
        REPO_AUDIT_ALLOWED_PATH_PREFIXES
    )


def _iter_repo_audit_files() -> list[Path]:
    files: list[Path] = []
    for root_name in REPO_AUDIT_SCAN_ROOTS:
        base = ROOT / root_name
        if not base.exists():
            continue
        files.extend(path for path in base.rglob("*") if path.is_file())
    return files


def validate_registry_tables() -> list[str]:
    errors: list[str] = []
    expected = FINAL_OFFICIAL_TARGETS
    if tuple(OFFICIAL_TARGETS) != expected:
        errors.append(
            "src/pcobra/cobra/transpilers/targets.py: OFFICIAL_TARGETS no coincide con el contrato final de 8 backends -> "
            f"official={tuple(OFFICIAL_TARGETS)}, expected={expected}"
        )
    if tuple(TIER1_TARGETS + TIER2_TARGETS) != expected:
        errors.append(
            "src/pcobra/cobra/transpilers/targets.py: OFFICIAL_TARGETS debe ser exactamente TIER1_TARGETS + TIER2_TARGETS -> "
            f"tier1={TIER1_TARGETS}, tier2={TIER2_TARGETS}, official={expected}"
        )
    if tuple(TRANSPILER_CLASS_PATHS) != expected:
        errors.append(
            "src/pcobra/cobra/transpilers/registry.py: TRANSPILER_CLASS_PATHS no coincide con OFFICIAL_TARGETS -> "
            f"registry={tuple(TRANSPILER_CLASS_PATHS)}, official={expected}"
        )
    if tuple(official_transpiler_targets()) != expected:
        errors.append(
            "src/pcobra/cobra/transpilers/registry.py: official_transpiler_targets() no coincide con OFFICIAL_TARGETS -> "
            f"registry={official_transpiler_targets()}, official={expected}"
        )
    if tuple(TRANSPILERS) != expected:
        errors.append(
            "src/pcobra/cobra/cli/commands/compile_cmd.py: TRANSPILERS no coincide con OFFICIAL_TARGETS -> "
            f"transpilers={tuple(TRANSPILERS)}, official={expected}"
        )
    if tuple(LANG_CHOICES) != expected:
        errors.append(
            "src/pcobra/cobra/cli/commands/compile_cmd.py: LANG_CHOICES no coincide con OFFICIAL_TARGETS -> "
            f"choices={tuple(LANG_CHOICES)}, official={expected}"
        )
    if tuple(BENCHMARKS_BACKENDS) != expected:
        errors.append(
            "src/pcobra/cobra/cli/commands/benchmarks_cmd.py: BACKENDS no coincide con OFFICIAL_TARGETS -> "
            f"benchmarks={tuple(BENCHMARKS_BACKENDS)}, official={expected}"
        )
    if official_transpiler_registry_literal() != EXPECTED_TRANSPILER_REGISTRY:
        errors.append(
            "src/pcobra/cobra/transpilers/registry.py: el registro oficial no coincide exactamente con los 8 backends esperados -> "
            f"registry={official_transpiler_registry_literal()}, expected={EXPECTED_TRANSPILER_REGISTRY}"
        )
    return errors


def validate_targeted_artifact_roots(
    official_targets: tuple[str, ...],
    reverse_scope: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []

    if tuple(official_targets) != FINAL_OFFICIAL_TARGETS:
        errors.append(
            "validate_targeted_artifact_roots: conjunto recibido distinto del contrato final -> "
            f"received={tuple(official_targets)}, expected={FINAL_OFFICIAL_TARGETS}"
        )

    found_forward_paths = {
        path.relative_to(ROOT).as_posix() for path in ROOT.rglob("to_*.py")
    }
    expected_forward_paths = set(EXPECTED_TRANSPILER_MODULES)
    for missing in sorted(expected_forward_paths - found_forward_paths):
        errors.append(
            f"{missing}: falta módulo oficial to_*.py para un backend canónico"
        )
    for extra in sorted(found_forward_paths - expected_forward_paths):
        errors.append(
            f"{extra}: módulo to_*.py extra fuera de política (posible backend 9 o alias interno expuesto)"
        )

    found_forward = {path.name for path in TRANSPILER_DIR.glob("to_*.py")}
    expected_forward = {Path(path).name for path in EXPECTED_TRANSPILER_MODULES}
    if found_forward != expected_forward:
        errors.append(
            f"{TRANSPILER_DIR.relative_to(ROOT).as_posix()}: directorio canónico desalineado -> "
            f"found={sorted(found_forward)}, expected={sorted(expected_forward)}"
        )

    expected_reverse = {
        f"from_{target}.py" for target in reverse_scope if target != "javascript"
    }
    expected_reverse.add("from_js.py")
    found_reverse = {path.name for path in REVERSE_DIR.glob("from_*.py")}
    for missing in sorted(expected_reverse - found_reverse):
        errors.append(
            f"{REVERSE_DIR.relative_to(ROOT).as_posix()}/{missing}: falta módulo reverse dentro del scope oficial"
        )
    for extra in sorted(found_reverse - expected_reverse):
        errors.append(
            f"{REVERSE_DIR.relative_to(ROOT).as_posix()}/{extra}: módulo reverse extra fuera del scope oficial"
        )

    found_golden_paths = {
        path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*.golden")
    }
    expected_golden_paths = set(EXPECTED_GOLDEN_FILES)
    for missing in sorted(expected_golden_paths - found_golden_paths):
        errors.append(f"{missing}: falta golden file oficial para un backend canónico")
    for extra in sorted(found_golden_paths - expected_golden_paths):
        errors.append(
            f"{extra}: golden file extra fuera de política (posible backend 9 no controlado)"
        )

    found_golden = {path.name for path in GOLDEN_DIR.glob("*.golden")}
    expected_golden = {Path(path).name for path in EXPECTED_GOLDEN_FILES}
    if found_golden != expected_golden:
        errors.append(
            f"{GOLDEN_DIR.relative_to(ROOT).as_posix()}: directorio canónico de goldens desalineado -> "
            f"found={sorted(found_golden)}, expected={sorted(expected_golden)}"
        )

    return errors


def validate_operational_checklist(official_targets: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    if not TARGET_CHECKLIST_PATH.exists():
        return [
            f"{TARGET_CHECKLIST_PATH.relative_to(ROOT).as_posix()}: checklist operativo obligatorio ausente"
        ]

    content = TARGET_CHECKLIST_PATH.read_text(encoding="utf-8")
    for block in CHECKLIST_BLOCKS:
        try:
            _extract_checklist_block(content, block)
        except RuntimeError as exc:
            errors.append(str(exc))
    if errors:
        return errors

    checklist_to_modules = set(_extract_checklist_block(content, "to_modules"))
    expected_to_modules = set(EXPECTED_TRANSPILER_MODULES)
    if checklist_to_modules != expected_to_modules:
        errors.append(
            f"{TARGET_CHECKLIST_PATH.relative_to(ROOT).as_posix()}: inventario to_*.py desalineado -> "
            f"checklist={sorted(checklist_to_modules)}, expected={sorted(expected_to_modules)}"
        )

    checklist_nodes = set(_extract_checklist_block(content, "nodes_dirs"))
    expected_nodes = {
        path.relative_to(ROOT).as_posix()
        for path in TRANSPILER_DIR.glob("*_nodes")
        if path.is_dir()
    }
    if checklist_nodes != expected_nodes:
        errors.append(
            f"{TARGET_CHECKLIST_PATH.relative_to(ROOT).as_posix()}: inventario *_nodes desalineado -> "
            f"checklist={sorted(checklist_nodes)}, expected={sorted(expected_nodes)}"
        )

    checklist_goldens = set(_extract_checklist_block(content, "golden_files"))
    expected_goldens = set(EXPECTED_GOLDEN_FILES)
    if checklist_goldens != expected_goldens:
        errors.append(
            f"{TARGET_CHECKLIST_PATH.relative_to(ROOT).as_posix()}: inventario de goldens desalineado -> "
            f"checklist={sorted(checklist_goldens)}, expected={sorted(expected_goldens)}"
        )

    checklist_cli_commands = tuple(
        _extract_checklist_block(content, "canonical_cli_commands")
    )
    if checklist_cli_commands != CANONICAL_POLICY_CLI_COMMANDS:
        errors.append(
            f"{TARGET_CHECKLIST_PATH.relative_to(ROOT).as_posix()}: set canónico CLI desalineado -> "
            f"checklist={checklist_cli_commands}, expected={CANONICAL_POLICY_CLI_COMMANDS}"
        )

    canonical_set = set(CANONICAL_POLICY_CLI_COMMANDS)
    cli_pattern = re.compile(r"`(cobra\s+[a-z0-9_-]+)`", re.IGNORECASE)
    for rel_path in CLI_POLICY_DOCS:
        path = ROOT / rel_path
        if not path.exists():
            errors.append(f"{rel_path}: documento de política CLI inexistente")
            continue
        policy_content = path.read_text(encoding="utf-8", errors="ignore")
        for match in cli_pattern.finditer(policy_content):
            command = match.group(1).lower()
            if command not in canonical_set:
                line_no = policy_content.count("\n", 0, match.start()) + 1
                errors.append(
                    f"{rel_path}:{line_no}: comando CLI fuera del set canónico de política -> {command}"
                )

    if tuple(official_targets) != FINAL_OFFICIAL_TARGETS:
        errors.append(
            "validate_operational_checklist: conjunto recibido distinto del contrato final -> "
            f"received={tuple(official_targets)}, expected={FINAL_OFFICIAL_TARGETS}"
        )

    phase_headers = PHASE_HEADER_PATTERN.findall(content)
    if len(phase_headers) != 5:
        errors.append(
            f"{TARGET_CHECKLIST_PATH.relative_to(ROOT).as_posix()}: se esperaban 5 fases explícitas y se encontraron {len(phase_headers)}"
        )

    phase_checkbox_matches = list(PHASE_CHECKBOX_PATTERN.finditer(content))
    if not phase_checkbox_matches:
        errors.append(
            f"{TARGET_CHECKLIST_PATH.relative_to(ROOT).as_posix()}: faltan checkboxes de estado para las fases"
        )
    else:
        pending_lines = [
            content[
                match.end() : (
                    content.find("\n", match.start())
                    if content.find("\n", match.start()) != -1
                    else len(content)
                )
            ].strip()
            for match in phase_checkbox_matches
            if match.group("mark") != "x" and match.group("mark") != "X"
        ]
        if pending_lines:
            preview = ", ".join(pending_lines[:2])
            errors.append(
                f"{TARGET_CHECKLIST_PATH.relative_to(ROOT).as_posix()}: checklist de fases incompleto, quedan tareas sin cerrar -> {preview}"
            )
    return errors


def validate_scan_roots(
    official_targets: tuple[str, ...],
    reverse_scope: tuple[str, ...],
) -> list[str]:
    del official_targets, reverse_scope
    errors: list[str] = []
    for path in PUBLIC_TEXT_PATHS:
        if not path.exists():
            errors.append(
                f"{path.relative_to(ROOT).as_posix()}: ruta pública vigilada inexistente"
            )
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        rel = (
            path.relative_to(ROOT).as_posix()
            if path.is_relative_to(ROOT)
            else str(path)
        )
        errors.extend(find_public_alias_errors(rel, content))
        errors.extend(find_non_python_sdk_promotion_errors(rel, content))
    return errors


def validate_public_documentation_alignment(
    official_targets: tuple[str, ...],
    reverse_scope: tuple[str, ...],
) -> list[str]:
    del reverse_scope
    errors: list[str] = []
    expected_targets = tuple(official_targets)

    targets_policy = ROOT / "docs/targets_policy.md"
    try:
        tier1 = _extract_targets_policy_tier(targets_policy, "Tier 1")
        if tier1 != tuple(TIER1_TARGETS):
            errors.append(
                f"docs/targets_policy.md: Tier 1 desalineado -> documented={tier1}, expected={tuple(TIER1_TARGETS)}"
            )
        tier2 = _extract_targets_policy_tier(targets_policy, "Tier 2")
        if tier2 != tuple(TIER2_TARGETS):
            errors.append(
                f"docs/targets_policy.md: Tier 2 desalineado -> documented={tier2}, expected={tuple(TIER2_TARGETS)}"
            )
    except RuntimeError as exc:
        errors.append(str(exc))

    for rel_path in DOC_TABLE_PATHS:
        path = ROOT / rel_path
        rows = _extract_doc_backend_rows(path)
        if not rows:
            errors.append(f"{rel_path}: no contiene filas de backends documentadas")
            continue
        documented_backends = {backend for _, backend in rows}
        for line_no, backend in rows:
            if backend not in expected_targets:
                errors.append(
                    f"{rel_path}:{line_no}: backend documentado fuera de política -> {backend}"
                )
        missing = [
            backend
            for backend in expected_targets
            if backend not in documented_backends
        ]
        if missing:
            errors.append(
                f"{rel_path}: faltan backends oficiales en la documentación pública -> {tuple(missing)}"
            )

    expected_matrix = {
        backend: {
            feature: BACKEND_COMPATIBILITY[backend][feature]
            for feature in ("tier", *CONTRACT_FEATURES)
        }
        for backend in expected_targets
    }
    for rel_path in (
        "docs/contrato_runtime_holobit.md",
        "docs/matriz_transpiladores.md",
    ):
        path = ROOT / rel_path
        parsed = _parse_backend_matrix_table(path)
        if parsed != expected_matrix:
            errors.append(
                f"{rel_path}: matriz contractual/Holobit desalineada con compatibility_matrix.py -> "
                f"documented={parsed}, expected={expected_matrix}"
            )

    for path in (*PUBLIC_RUNTIME_POLICY_PATHS, *HOLOBIT_MATRIX_DOC_PATHS):
        rel = (
            path.relative_to(ROOT).as_posix()
            if path.is_relative_to(ROOT)
            else str(path)
        )
        content = path.read_text(encoding="utf-8", errors="ignore")
        for match in FORBIDDEN_NON_PYTHON_SDK_PROMOTION.finditer(content):
            backend = match.group("backend").lower()
            line_no = content.count("\n", 0, match.start()) + 1
            errors.append(
                f"{rel}:{line_no}: promoción pública inválida del contrato SDK/Holobit -> backend={backend} debe seguir en partial/no full fuera de python"
            )
    return errors


def validate_critical_docs_generated_lists(
    official_targets: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    expected_csv = ", ".join(official_targets)
    expected_rst_csv = ", ".join(f"``{target}``" for target in official_targets)

    for rel_path, required_fragments in CRITICAL_DOCS_GENERATED_CONTRACT.items():
        path = ROOT / rel_path
        if not path.exists():
            errors.append(f"{rel_path}: documento crítico ausente para validación CI")
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for fragment in required_fragments:
            if fragment not in content:
                errors.append(
                    f"{rel_path}: falta include/marcador canónico requerido -> {fragment}"
                )

        for line_no, line in enumerate(content.splitlines(), start=1):
            lowered = line.lower()
            if expected_csv in lowered or expected_rst_csv in lowered:
                if "generated" in lowered:
                    continue
                errors.append(
                    f"{rel_path}:{line_no}: lista manual de targets detectada en doc crítica; debe derivarse por include/fragmento generado"
                )
    return errors


def validate_python_policy_literals(
    official_targets: tuple[str, ...],
    **_: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    expected = FINAL_OFFICIAL_TARGETS
    policy = read_target_policy()

    if tuple(official_targets) != expected:
        errors.append(
            "validate_python_policy_literals: conjunto recibido distinto del contrato final -> "
            f"received={tuple(official_targets)}, expected={expected}"
        )
    if tuple(policy["official_targets"]) != expected:
        errors.append(
            "scripts/targets_policy_common.py: read_target_policy()['official_targets'] no coincide con los 8 oficiales -> "
            f"policy={tuple(policy['official_targets'])}, expected={expected}"
        )
    if tuple(policy["tier1_targets"]) + tuple(policy["tier2_targets"]) != expected:
        errors.append(
            "scripts/targets_policy_common.py: read_target_policy() no conserva la partición tier1+tier2 -> "
            f"tier1={tuple(policy['tier1_targets'])}, tier2={tuple(policy['tier2_targets'])}, expected={expected}"
        )
    if tuple(SDK_COMPATIBLE_TARGETS) != ("python",):
        errors.append(
            "src/pcobra/cobra/cli/target_policies.py: SDK_COMPATIBLE_TARGETS debe ser exclusivamente ('python',) -> "
            f"actual={tuple(SDK_COMPATIBLE_TARGETS)}"
        )
    if tuple(SDK_FULL_BACKENDS) != ("python",):
        errors.append(
            "src/pcobra/cobra/transpilers/compatibility_matrix.py: SDK_FULL_BACKENDS debe ser exclusivamente ('python',) -> "
            f"actual={tuple(SDK_FULL_BACKENDS)}"
        )
    try:
        validate_backend_compatibility_contract()
    except RuntimeError as exc:
        errors.append(f"src/pcobra/cobra/transpilers/compatibility_matrix.py: {exc}")
    for backend in FINAL_OFFICIAL_TARGETS:
        for feature in CONTRACT_FEATURES:
            level = BACKEND_COMPATIBILITY[backend][feature]
            gaps = BACKEND_FEATURE_GAPS[backend][feature]
            if level == "full" and gaps:
                errors.append(
                    "src/pcobra/cobra/transpilers/compatibility_matrix.py: "
                    f"{backend}.{feature} está en full pero declara gaps={gaps}"
                )
            if level == "partial" and not gaps:
                errors.append(
                    "src/pcobra/cobra/transpilers/compatibility_matrix.py: "
                    f"{backend}.{feature} está en partial sin gaps explícitos"
                )
    return errors


def validate_retired_targets_guardrail() -> list[str]:
    """Evita fugas de rutas históricas retiradas en superficies públicas/operativas."""
    errors: list[str] = []

    for rel_path in DOC_INDEX_GUARDRAIL_PATHS:
        path = ROOT / rel_path
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if RETIRED_TARGETS_LITERAL in content:
            errors.append(
                f"{rel_path}: fuga de histórico retirado en índice/documentación pública ({RETIRED_TARGETS_LITERAL})"
            )

    for rel_path in PACKAGING_GUARDRAIL_PATHS:
        path = ROOT / rel_path
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if RETIRED_TARGETS_LITERAL in content:
            errors.append(
                f"{rel_path}: fuga de histórico retirado en rutas de packaging ({RETIRED_TARGETS_LITERAL})"
            )

    for root_name in IMPORT_GUARDRAIL_SCAN_ROOTS:
        base = ROOT / root_name
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT).as_posix()
            if _is_historical_repo_path(rel):
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
            if RETIRED_TARGETS_LITERAL in content:
                offset = content.find(RETIRED_TARGETS_LITERAL)
                line_no = content.count("\n", 0, offset) + 1
                errors.append(
                    f"{rel}:{line_no}: fuga de histórico retirado en árbol operativo ({RETIRED_TARGETS_LITERAL})"
                )
            for pattern in IMPORT_GUARDRAIL_PATTERNS:
                for match in pattern.finditer(content):
                    line_no = content.count("\n", 0, match.start()) + 1
                    errors.append(
                        f"{rel}:{line_no}: import/ruta operativa no permitida hacia histórico retirado"
                    )
    return errors


def validate_final_backend_repo_audit() -> list[str]:
    errors: list[str] = []
    for path in _iter_repo_audit_files():
        rel = (
            path.relative_to(ROOT).as_posix()
            if path.is_relative_to(ROOT)
            else str(path)
        )
        if _is_historical_repo_path(rel):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern, description in REPO_AUDIT_FORBIDDEN_TERMS:
            for match in pattern.finditer(content):
                line_no = content.count("\n", 0, match.start()) + 1
                errors.append(
                    f"{rel}:{line_no}: referencia fuera del conjunto final -> {description}"
                )
        for pattern, alias in REPO_AUDIT_FORBIDDEN_ALIAS_LITERALS:
            for match in pattern.finditer(content):
                line_no = content.count("\n", 0, match.start()) + 1
                errors.append(
                    f"{rel}:{line_no}: alias legacy literal fuera del conjunto final -> {alias}"
                )
    return errors


def _run_stage(name: str, errors: list[str]) -> int | None:
    if not errors:
        return None
    print("❌ Validación CI de targets: FALLÓ", file=sys.stderr)
    print(f" - etapa: {name}", file=sys.stderr)
    print(f" - {errors[0]}", file=sys.stderr)
    if len(errors) > 1:
        print(
            f" - y {len(errors) - 1} desalineación(es) adicional(es) en la misma etapa",
            file=sys.stderr,
        )
    return 1


def main() -> int:
    official_targets = tuple(OFFICIAL_TARGETS)
    reverse_scope = tuple(REVERSE_SCOPE_LANGUAGES)
    stages = (
        ("registros canónicos", validate_registry_tables()),
        ("checklist operativo", validate_operational_checklist(official_targets)),
        (
            "artefactos dirigidos",
            validate_targeted_artifact_roots(official_targets, reverse_scope),
        ),
        ("escaneo público", validate_scan_roots(official_targets, reverse_scope)),
        (
            "documentación pública",
            validate_public_documentation_alignment(official_targets, reverse_scope),
        ),
        (
            "docs críticas generadas",
            validate_critical_docs_generated_lists(official_targets),
        ),
        (
            "contrato Python/Holobit/SDK",
            validate_python_policy_literals(official_targets),
        ),
        ("guard-rail histórico retirado", validate_retired_targets_guardrail()),
        ("auditoría de repo", validate_final_backend_repo_audit()),
    )
    for stage_name, errors in stages:
        result = _run_stage(stage_name, errors)
        if result is not None:
            return result

    print("✅ Validación CI de targets: OK")
    print(f"   OFFICIAL_TARGETS: {', '.join(official_targets)}")
    print(f"   REVERSE_SCOPE_LANGUAGES: {', '.join(reverse_scope)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
