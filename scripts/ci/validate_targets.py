#!/usr/bin/env python3
"""Validaciones anti-regresión para targets oficiales.

Checks principales:
1) Igualdad exacta entre ``OFFICIAL_TARGETS`` y las claves efectivas de ``TRANSPILERS``.
2) No existen módulos ``to_*.py`` o ``from_*.py`` fuera del alcance oficialmente definido.
3) Scripts auxiliares, documentación, tests y ejemplos no reintroducen imports reverse,
   módulos retirados ni nombres públicos no canónicos salvo en rutas históricas acotadas.
4) ``transpilar-inverso`` expone únicamente orígenes reverse canónicos y destinos dentro
   de ``OFFICIAL_TARGETS``.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
TRANSPILER_DIR = ROOT / "src/pcobra/cobra/transpilers/transpiler"
REVERSE_DIR = ROOT / "src/pcobra/cobra/transpilers/reverse"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pcobra.cobra.cli.commands.compile_cmd import TRANSPILERS
from pcobra.cobra.cli.commands.transpilar_inverso_cmd import (
    DESTINO_CHOICES,
    ORIGIN_CHOICES,
    REVERSE_TRANSPILERS,
)
from pcobra.cobra.transpilers.reverse import REVERSE_SCOPE_LANGUAGES
from pcobra.cobra.transpilers.targets import TIER1_TARGETS, TIER2_TARGETS
from pcobra.cobra.transpilers.reverse.policy import normalize_reverse_language
from scripts.targets_policy_common import (
    HOLOBIT_MATRIX_DOC_PATHS,
    HOLOBIT_PUBLIC_CONTRACT_PATHS,
    LEGACY_ALIAS_ALLOWLIST,
    NON_CANONICAL_PUBLIC_NAMES,
    OUT_OF_POLICY_LANGUAGE_TERMS,
    PUBLIC_TEXT_PATHS,
    PUBLIC_TEXT_PATH_STRS,
    PUBLIC_RUNTIME_POLICY_PATHS,
    VALIDATION_SCAN_PATHS,
    build_legacy_alias_patterns,
    read_target_policy,
)

SCAN_ROOTS = VALIDATION_SCAN_PATHS

GENERATED_PATH_PARTS = (
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    "docs/_build/",
)

BINARY_OR_GENERATED_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".svgz",
    ".ico",
    ".zip",
    ".gz",
    ".tar",
    ".tgz",
    ".bz2",
    ".xz",
    ".7z",
    ".jar",
    ".class",
    ".o",
    ".a",
    ".so",
    ".dylib",
    ".dll",
    ".exe",
    ".wasm",
    ".pyc",
    ".pyo",
    ".pyd",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".mp3",
    ".mp4",
    ".mov",
    ".avi",
    ".ipynb",
}

ALLOWED_HISTORICAL_PATH_PREFIXES = (
    "docs/historico/",
    "docs/experimental/",
)

REMOVED_REVERSE_LANGUAGES = ("c", "cpp", "go", "rust", "wasm", "asm")
REMOVED_REVERSE_MODULE_PATTERNS = tuple(
    f"from_{language}.py" for language in REMOVED_REVERSE_LANGUAGES
)
REMOVED_TRANSPILER_MODULE_PATTERNS = ("to_c.py",)
REMOVED_BACKEND_NAME_PATTERNS: dict[str, re.Pattern[str]] = {
    "c": re.compile(
        r"(?<![\w.-])(?:--(?:tipo|tipos|backend|destino)(?:=|\s+)|`)(c)(?:`)?(?![\w.-])",
        re.IGNORECASE,
    ),
    "reverse-wasm": re.compile(r"(?<![\w.-])(reverse-wasm)(?![\w.-])", re.IGNORECASE),
}
REMOVED_C_CONDITIONAL_PATTERNS: dict[str, re.Pattern[str]] = {
    "lang==c": re.compile(
        r"\b(?:lang|language|lenguaje|backend|target|destino)\s*==\s*['\"]c['\"]"
    ),
    "lang!=c": re.compile(
        r"\b(?:lang|language|lenguaje|backend|target|destino)\s*!=\s*['\"]c['\"]"
    ),
    "c-dict-key": re.compile(r"(?:\{|,)\s*['\"]c['\"]\s*:"),
    "c-extension": re.compile(r"['\"]\.c['\"]"),
}
REVERSE_IMPORT_PREFIXES = (
    "cobra.transpilers.reverse.from_",
    "pcobra.cobra.transpilers.reverse.from_",
)

EXPERIMENTAL_DOCS = (
    ROOT / "docs/experimental/README.md",
    ROOT / "docs/experimental/llvm_prototype.md",
    ROOT / "docs/experimental/construcciones_llvm_ir.md",
    ROOT / "docs/experimental/soporte_latex.md",
    ROOT / "docs/experimental/limitaciones_wasm_reverse.md",
)

EXPERIMENTAL_DOC_REQUIRED_MARKERS = (
    "experimental",
    "política",
)

UNOFFICIAL_PUBLIC_TARGET_PATTERNS: dict[str, re.Pattern[str]] = {
    "hololang-cli-target": re.compile(
        r"--(?:backend|destino)(?:=|\s+)(hololang)(?![\w.-])",
        re.IGNORECASE,
    ),
    "llvm-cli-target": re.compile(
        r"--(?:backend|destino)(?:=|\s+)(llvm)(?![\w.-])",
        re.IGNORECASE,
    ),
    "latex-cli-target": re.compile(
        r"--(?:backend|destino|origen)(?:=|\s+)(latex)(?![\w.-])",
        re.IGNORECASE,
    ),
    "hololang-public-target-claim": re.compile(
        r"(?:target|destino)(?:\s+can[oó]nico|\s+oficial|\s+de\s+salida)?\s+[`']?(hololang)[`']?",
        re.IGNORECASE,
    ),
}

PUBLIC_NAME_PATTERNS: dict[str, re.Pattern[str]] = {
    alias: re.compile(rf"(?<![\w.+-])({re.escape(alias)})(?![\w.+-])", re.IGNORECASE)
    for alias in sorted(
        set(NON_CANONICAL_PUBLIC_NAMES)
        | set(read_target_policy()["legacy_aliases"])
        | set(OUT_OF_POLICY_LANGUAGE_TERMS)
    )
}

SKIPPED_SCAN_REL_PATHS = frozenset(
    {
        "scripts/ci/validate_targets.py",
        "scripts/validate_targets_policy.py",
        "scripts/targets_policy_common.py",
        "scripts/lint_legacy_aliases.py",
    }
)

POLICY_LITERAL_TARGET_NAMES = frozenset(
    {
        "SUPPORTED_TARGETS",
        "OFFICIAL_TARGETS",
        "OFFICIAL_RUNTIME_TARGETS",
        "DOCKER_EXECUTABLE_TARGETS",
        "VERIFICATION_EXECUTABLE_TARGETS",
        "TRANSPILATION_ONLY_TARGETS",
    }
)
POLICY_LITERAL_PREFIX_NAMES = frozenset(
    {
        "CLI_OFFICIAL_RUNTIME_TARGETS",
        "CLI_TRANSPILATION_ONLY_TARGETS",
    }
)

PUBLIC_POLICY_LIST_PATTERNS: dict[str, tuple[re.Pattern[str], str]] = {
    "official_targets": (
        re.compile(r"targets oficiales de transpilación", re.IGNORECASE),
        "targets oficiales de transpilación",
    ),
    "official_runtime_targets": (
        re.compile(r"targets con runtime oficial", re.IGNORECASE),
        "targets con runtime oficial",
    ),
    "reverse_scope_languages": (
        re.compile(r"or[ií]genes de transpilaci[oó]n inversa", re.IGNORECASE),
        "orígenes reverse oficiales",
    ),
    "official_runtime_targets_alt": (
        re.compile(r"runtime oficial en contenedor/sandbox", re.IGNORECASE),
        "runtime oficial en contenedor/sandbox",
    ),
    "transpilation_only_targets": (
        re.compile(r"targets oficiales solo de transpilaci[oó]n", re.IGNORECASE),
        "targets oficiales solo de transpilación",
    ),
    "verification_targets": (
        re.compile(r"verificaci[oó]n ejecutable expl[ií]cita en cli", re.IGNORECASE),
        "verificación ejecutable explícita en CLI",
    ),
}

FORBIDDEN_NON_PYTHON_HOLOBIT_FULL_CLAIM = re.compile(
    r"(javascript|rust|wasm|go|cpp|java|asm).{0,120}"
    r"(holobit|proyectar|transformar|graficar|corelibs|standard_library).{0,80}"
    r"(full|compatibilidad total con holobit sdk|compatibilidad sdk completa)",
    re.IGNORECASE | re.DOTALL,
)


def read_transpiler_registry_keys() -> tuple[str, ...]:
    return tuple(TRANSPILERS.keys())


def _iter_scan_files() -> tuple[Path, ...]:
    files: list[Path] = []
    for path in SCAN_ROOTS:
        if not path.exists():
            continue
        if path.is_file():
            files.append(path)
            continue
        files.extend(candidate for candidate in path.rglob("*") if candidate.is_file())
    return tuple(sorted(files))


def _is_generated_or_binary(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if any(part in rel for part in GENERATED_PATH_PARTS):
        return True
    if path.suffix.lower() in BINARY_OR_GENERATED_SUFFIXES:
        return True

    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return True
    return b"\x00" in sample


def _is_allowed_historical_path(rel: str) -> bool:
    return any(rel.startswith(prefix) for prefix in ALLOWED_HISTORICAL_PATH_PREFIXES)


def _extract_backtick_targets(line: str, *, allowed_names: set[str]) -> tuple[str, ...]:
    return tuple(
        match.lower()
        for match in re.findall(r"`([^`]+)`", line)
        if match.lower() in allowed_names
    )


def _parse_backend_matrix_table(path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("| `"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        backend = cells[0].strip("`")
        rows[backend] = {
            "tier": cells[1].lower().replace(" ", ""),
            "holobit": cells[2].split()[-1],
            "proyectar": cells[3].split()[-1],
            "transformar": cells[4].split()[-1],
            "graficar": cells[5].split()[-1],
            "corelibs": cells[6].split()[-1],
            "standard_library": cells[7].split()[-1],
        }
    return rows


def _literal_string_collection(node: ast.AST | None) -> tuple[str, ...] | None:
    if not isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return None

    values: list[str] = []
    for element in node.elts:
        if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
            return None
        values.append(element.value)
    return tuple(values)


def _assignment_target_names(node: ast.Assign | ast.AnnAssign) -> tuple[str, ...]:
    if isinstance(node, ast.Assign):
        return tuple(
            target.id for target in node.targets if isinstance(target, ast.Name)
        )
    if isinstance(node.target, ast.Name):
        return (node.target.id,)
    return ()


def _expected_collection_for_name(
    name: str,
    *,
    official_targets: tuple[str, ...],
    official_runtime_targets: tuple[str, ...],
    transpilation_only_targets: tuple[str, ...],
    verification_targets: tuple[str, ...],
) -> tuple[str, ...] | None:
    if name == "SUPPORTED_TARGETS" or name == "OFFICIAL_TARGETS":
        return official_targets
    if name in {"OFFICIAL_RUNTIME_TARGETS", "DOCKER_EXECUTABLE_TARGETS"}:
        return official_runtime_targets
    if name == "TRANSPILATION_ONLY_TARGETS":
        return transpilation_only_targets
    if name == "VERIFICATION_EXECUTABLE_TARGETS":
        return verification_targets
    return None


def validate_transpiler_modules(official: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    allowed_suffixes = {
        "javascript" if target == "javascript" else target for target in official
    }
    alias_suffix_map = {"js": "javascript"}

    found_canonical_suffixes: set[str] = set()

    for file_path in sorted(TRANSPILER_DIR.glob("to_*.py")):
        suffix = file_path.stem.removeprefix("to_")
        canonical = alias_suffix_map.get(suffix, suffix)
        if canonical not in official:
            errors.append(
                f"{file_path.relative_to(ROOT)}: módulo fuera de OFFICIAL_TARGETS -> to_{suffix}.py"
            )
            continue
        found_canonical_suffixes.add(canonical)
        if suffix not in allowed_suffixes and suffix not in alias_suffix_map:
            errors.append(
                f"{file_path.relative_to(ROOT)}: sufijo no canónico para target oficial -> to_{suffix}.py"
            )

    if found_canonical_suffixes != set(official):
        errors.append(
            "TRANSPILER_DIR: los módulos to_*.py no cubren exactamente OFFICIAL_TARGETS -> "
            f"found={sorted(found_canonical_suffixes)}, official={list(official)}"
        )

    return errors


def validate_no_legacy_aliases_in_public_paths(
    legacy_aliases: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    patterns = build_legacy_alias_patterns(legacy_aliases)
    if not patterns:
        return errors

    for path in PUBLIC_TEXT_PATHS:
        if not path.exists():
            continue
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        allow_patterns = LEGACY_ALIAS_ALLOWLIST.get(rel, ())

        for line_no, line in enumerate(text.splitlines(), start=1):
            for pat in patterns:
                match = pat.search(line)
                if not match:
                    continue
                if any(ap.search(line) for ap in allow_patterns):
                    continue
                errors.append(
                    f"{rel}:{line_no}: alias legacy en ruta pública -> {match.group(1)}"
                )

    return errors


def validate_experimental_docs_scope() -> list[str]:
    errors: list[str] = []

    for path in EXPERIMENTAL_DOCS:
        rel = path.relative_to(ROOT).as_posix()
        if not path.exists():
            errors.append(
                f"{rel}: falta documentación experimental segregada requerida"
            )
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for required in EXPERIMENTAL_DOC_REQUIRED_MARKERS:
            if required not in lowered:
                errors.append(
                    f"{rel}: falta marcador obligatorio de documentación experimental -> {required}"
                )

    old_public_paths = (
        ROOT / "docs/llvm_prototype.md",
        ROOT / "docs/construcciones_llvm_ir.md",
        ROOT / "docs/soporte_latex.md",
        ROOT / "docs/limitaciones_wasm_reverse.md",
    )
    for old_path in old_public_paths:
        if old_path.exists():
            errors.append(
                f"{old_path.relative_to(ROOT).as_posix()}: el documento debe vivir en docs/experimental/"
            )

    for path in PUBLIC_TEXT_PATHS:
        if not path.exists():
            continue
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for name, pattern in UNOFFICIAL_PUBLIC_TARGET_PATTERNS.items():
                match = pattern.search(line)
                if match:
                    errors.append(
                        f"{rel}:{line_no}: referencia pública a target/pipeline no oficial ({name}) -> {match.group(1)}"
                    )

    return errors




def validate_policy_tiers(policy: dict[str, object]) -> list[str]:
    errors: list[str] = []
    tier1_targets = tuple(policy["tier1_targets"])
    tier2_targets = tuple(policy["tier2_targets"])
    official_targets = tuple(policy["official_targets"])
    expected = tuple((*TIER1_TARGETS, *TIER2_TARGETS))

    if tier1_targets != TIER1_TARGETS:
        errors.append(
            f"tier1_targets desalineado con targets.py -> {tier1_targets} (esperado: {TIER1_TARGETS})"
        )
    if tier2_targets != TIER2_TARGETS:
        errors.append(
            f"tier2_targets desalineado con targets.py -> {tier2_targets} (esperado: {TIER2_TARGETS})"
        )
    if official_targets != expected:
        errors.append(
            f"official_targets desalineado con tier1+tier2 -> {official_targets} (esperado: {expected})"
        )
    return errors

def validate_reverse_cli_contract(
    official_targets: tuple[str, ...],
    reverse_scope_languages: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []

    if tuple(DESTINO_CHOICES) != tuple(official_targets):
        errors.append(
            "transpilar-inverso: DESTINO_CHOICES no coincide exactamente con "
            f"OFFICIAL_TARGETS -> destino={DESTINO_CHOICES}, official={official_targets}"
        )

    if tuple(ORIGIN_CHOICES) != tuple(sorted(reverse_scope_languages)):
        errors.append(
            "transpilar-inverso: ORIGIN_CHOICES no coincide con REVERSE_SCOPE_LANGUAGES "
            f"-> origen={ORIGIN_CHOICES}, reverse={tuple(sorted(reverse_scope_languages))}"
        )

    reverse_registry = tuple(REVERSE_TRANSPILERS.keys())
    extras = sorted(set(reverse_registry) - set(reverse_scope_languages))
    if extras:
        errors.append(
            "transpilar-inverso: REVERSE_TRANSPILERS expone aliases/no canónicos -> "
            + ", ".join(extras)
        )

    return errors


def validate_public_policy_lists(
    official_targets: tuple[str, ...],
    reverse_scope_languages: tuple[str, ...],
    *,
    official_runtime_targets: tuple[str, ...],
    transpilation_only_targets: tuple[str, ...],
    verification_targets: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    allowed_names = set(official_targets) | set(official_runtime_targets) | set(
        reverse_scope_languages
    ) | set(transpilation_only_targets) | set(verification_targets)
    expected_values = {
        "official_targets": set(official_targets),
        "official_runtime_targets": set(official_runtime_targets),
        "official_runtime_targets_alt": set(official_runtime_targets),
        "reverse_scope_languages": set(reverse_scope_languages),
        "transpilation_only_targets": set(transpilation_only_targets),
        "verification_targets": set(verification_targets),
    }

    for path in PUBLIC_RUNTIME_POLICY_PATHS:
        if not path.exists():
            continue
        rel = path.relative_to(ROOT).as_posix()
        for line_no, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for key, (pattern, label) in PUBLIC_POLICY_LIST_PATTERNS.items():
                if not pattern.search(line):
                    continue
                line_targets = _extract_backtick_targets(line, allowed_names=allowed_names)
                if not line_targets:
                    continue
                found = set(line_targets)
                expected = expected_values[key]
                if found != expected:
                    errors.append(
                        f"{rel}:{line_no}: lista pública desalineada para {label} -> "
                        f"{sorted(found)} (esperado: {sorted(expected)})"
                    )
    return errors


def validate_holobit_public_contract() -> list[str]:
    errors: list[str] = []
    expected = read_target_policy()["compatibility_matrix"]

    for path in HOLOBIT_MATRIX_DOC_PATHS:
        if not path.exists():
            continue
        rel = path.relative_to(ROOT).as_posix()
        found = _parse_backend_matrix_table(path)
        if found != expected:
            errors.append(
                f"{rel}: matriz contractual Holobit desalineada con compatibility_matrix.py"
            )

    for path in HOLOBIT_PUBLIC_CONTRACT_PATHS:
        if not path.exists():
            continue
        rel = path.relative_to(ROOT).as_posix()
        content = path.read_text(encoding="utf-8")
        for match in FORBIDDEN_NON_PYTHON_HOLOBIT_FULL_CLAIM.finditer(content):
            errors.append(
                f"{rel}: claim público de compatibilidad Holobit fuera de matriz contractual -> {match.group(1)}"
            )

    return errors


def validate_module_file_scope(
    official_targets: tuple[str, ...],
    reverse_scope_languages: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    official_modules = {
        f"to_{target}.py" for target in official_targets if target != "javascript"
    }
    official_modules.add("to_js.py")
    reverse_modules = {
        f"from_{target}.py"
        for target in reverse_scope_languages
        if target != "javascript"
    }
    reverse_modules.add("from_js.py")

    for path in sorted(ROOT.rglob("to_*.py")):
        rel = path.relative_to(ROOT).as_posix()
        if any(part in rel for part in GENERATED_PATH_PARTS):
            continue
        if path.parent != TRANSPILER_DIR or path.name not in official_modules:
            errors.append(
                f"{rel}: archivo to_*.py fuera del alcance oficial o en ubicación no permitida"
            )

    for path in sorted(ROOT.rglob("from_*.py")):
        rel = path.relative_to(ROOT).as_posix()
        if any(part in rel for part in GENERATED_PATH_PARTS):
            continue
        if path.parent != REVERSE_DIR or path.name not in reverse_modules:
            errors.append(
                f"{rel}: archivo from_*.py fuera del alcance reverse oficial o en ubicación no permitida"
            )

    return errors


def validate_python_policy_literals(
    official_targets: tuple[str, ...],
    *,
    official_runtime_targets: tuple[str, ...],
    transpilation_only_targets: tuple[str, ...],
    verification_targets: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    watched_prefixes = (
        "tests/utils/",
        "tests/performance/",
        "tests/integration/",
    )

    for path in _iter_scan_files():
        rel = path.relative_to(ROOT).as_posix()
        if (
            path.suffix != ".py"
            or not rel.startswith(watched_prefixes)
            or _is_generated_or_binary(path)
        ):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue

        for node in tree.body:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            literal = _literal_string_collection(getattr(node, "value", None))
            if literal is None:
                continue
            for name in _assignment_target_names(node):
                if name not in POLICY_LITERAL_TARGET_NAMES | POLICY_LITERAL_PREFIX_NAMES:
                    continue
                expected = _expected_collection_for_name(
                    name.removeprefix("CLI_"),
                    official_targets=official_targets,
                    official_runtime_targets=official_runtime_targets,
                    transpilation_only_targets=transpilation_only_targets,
                    verification_targets=verification_targets,
                )
                if expected is None:
                    continue
                if tuple(literal) != tuple(expected):
                    errors.append(
                        f"{rel}:{getattr(node, 'lineno', 1)}: lista hardcodeada desalineada con target_policies.py -> "
                        f"{name}={literal} (esperado: {expected})"
                    )

    return errors


def _collect_python_reverse_imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set()

    imports: set[str] = set()
    for node in ast.walk(tree):
        modules: list[str] = []
        if isinstance(node, ast.ImportFrom) and node.module:
            modules = [node.module]
        elif isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]

        for module in modules:
            for prefix in REVERSE_IMPORT_PREFIXES:
                if module.startswith(prefix):
                    imports.add(module.removeprefix(prefix))
    return imports


def validate_scan_roots(
    official_targets: tuple[str, ...],
    reverse_scope_languages: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    allowed_reverse = set(reverse_scope_languages)
    public_name_map = dict(NON_CANONICAL_PUBLIC_NAMES)
    public_name_map.update(
        {
            alias: canonical
            for alias, canonical in read_target_policy()["legacy_aliases"].items()
        }
    )

    for path in _iter_scan_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel in SKIPPED_SCAN_REL_PATHS or _is_generated_or_binary(path):
            continue

        historical_path = _is_allowed_historical_path(rel)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for line_no, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()

            if not historical_path:
                for removed_module in (
                    REMOVED_REVERSE_MODULE_PATTERNS + REMOVED_TRANSPILER_MODULE_PATTERNS
                ):
                    if removed_module in lowered:
                        errors.append(
                            f"{rel}:{line_no}: referencia a módulo retirado -> {removed_module}"
                        )

                for retired_name, pattern in REMOVED_BACKEND_NAME_PATTERNS.items():
                    match = pattern.search(line)
                    if match:
                        errors.append(
                            f"{rel}:{line_no}: referencia a backend retirado -> {retired_name}"
                        )

                for pattern_name, pattern in REMOVED_C_CONDITIONAL_PATTERNS.items():
                    if pattern.search(line):
                        errors.append(
                            f"{rel}:{line_no}: rama/helper/tabla fuera de política para backend retirado 'c' -> {pattern_name}"
                        )

                if rel in PUBLIC_TEXT_PATH_STRS:
                    for alias, pattern in PUBLIC_NAME_PATTERNS.items():
                        match = pattern.search(line)
                        if not match:
                            continue
                        canonical = public_name_map.get(alias)
                        if canonical is not None:
                            errors.append(
                                f"{rel}:{line_no}: nombre público no canónico -> {match.group(1)} (usar: {canonical})"
                            )
                        else:
                            errors.append(
                                f"{rel}:{line_no}: backend fuera de política en texto público -> {match.group(1)}"
                            )

        if path.suffix != ".py" or historical_path:
            continue

        for imported in sorted(_collect_python_reverse_imports(path)):
            canonical = (
                "javascript"
                if imported == "js"
                else normalize_reverse_language(imported)
            )
            if canonical not in allowed_reverse:
                errors.append(
                    f"{rel}: import reverse fuera del alcance oficial -> from_{imported}"
                )

    return errors


def main() -> int:
    errors: list[str] = []

    policy = read_target_policy()
    errors.extend(validate_policy_tiers(policy))
    official_targets = policy["official_targets"]
    official_runtime_targets = policy["official_runtime_targets"]
    verification_targets = policy["verification_targets"]
    transpilation_only_targets = policy["transpilation_only_targets"]
    legacy_aliases = policy["legacy_aliases"]
    transpilers = read_transpiler_registry_keys()

    if transpilers != official_targets:
        missing_in_registry = sorted(set(official_targets) - set(transpilers))
        extra_in_registry = sorted(set(transpilers) - set(official_targets))
        errors.append("Desalineación OFFICIAL_TARGETS vs TRANSPILERS:")
        errors.append(f"  - OFFICIAL_TARGETS: {', '.join(official_targets)}")
        errors.append(f"  - TRANSPILERS: {', '.join(transpilers)}")
        if missing_in_registry:
            errors.append(
                f"  - faltan en TRANSPILERS: {', '.join(missing_in_registry)}"
            )
        if extra_in_registry:
            errors.append(f"  - sobran en TRANSPILERS: {', '.join(extra_in_registry)}")

    reverse_scope = tuple(REVERSE_SCOPE_LANGUAGES)
    errors.extend(validate_transpiler_modules(official_targets))
    errors.extend(validate_no_legacy_aliases_in_public_paths(legacy_aliases))
    errors.extend(validate_experimental_docs_scope())
    errors.extend(validate_reverse_cli_contract(official_targets, reverse_scope))
    errors.extend(
        validate_public_policy_lists(
            official_targets,
            reverse_scope,
            official_runtime_targets=official_runtime_targets,
            transpilation_only_targets=transpilation_only_targets,
            verification_targets=verification_targets,
        )
    )
    errors.extend(validate_holobit_public_contract())
    errors.extend(validate_module_file_scope(official_targets, reverse_scope))
    errors.extend(
        validate_python_policy_literals(
            official_targets,
            official_runtime_targets=official_runtime_targets,
            transpilation_only_targets=transpilation_only_targets,
            verification_targets=verification_targets,
        )
    )
    errors.extend(validate_scan_roots(official_targets, reverse_scope))

    if errors:
        print("❌ Validación anti-regresión de targets: FALLÓ", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)
        return 1

    print("✅ Validación anti-regresión de targets: OK")
    print(f"   Tier 1: {', '.join(policy['tier1_targets'])}")
    print(f"   Tier 2: {', '.join(policy['tier2_targets'])}")
    print(f"   OFFICIAL_TARGETS: {', '.join(official_targets)}")
    print(f"   Runtime oficial: {', '.join(official_runtime_targets)}")
    print(f"   Solo transpilación: {', '.join(transpilation_only_targets)}")
    print(f"   Verificación ejecutable: {', '.join(verification_targets)}")
    print(f"   TRANSPILERS: {', '.join(transpilers)}")
    print(f"   Reverse scope: {', '.join(reverse_scope)}")
    print(
        "   Allowlist histórica: "
        + ", ".join(ALLOWED_HISTORICAL_PATH_PREFIXES)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
