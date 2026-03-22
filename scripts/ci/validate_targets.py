#!/usr/bin/env python3
"""Validaciones anti-regresión para targets oficiales.

Checks principales:
1) Igualdad exacta entre ``OFFICIAL_TARGETS`` y las claves efectivas de ``TRANSPILERS``.
2) No existen módulos ``to_*.py`` o ``from_*.py`` fuera del alcance oficialmente definido.
3) Scripts auxiliares, documentación, tests y ejemplos no reintroducen imports reverse,
   módulos retirados ni nombres públicos no canónicos salvo en rutas históricas acotadas.
4) ``transpilar-inverso`` expone únicamente orígenes reverse canónicos y destinos dentro
   de ``OFFICIAL_TARGETS``.
5) Árboles vigilados (transpilers, reverse, golden, benchmarks y docs públicas) no pueden
   incorporar artefactos, imports o aliases asociados a backends no oficiales o retirados.
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
REVERSE_POLICY_PATH = REVERSE_DIR / "policy.py"
TRANSPILER_REGISTRY_PATH = ROOT / "src/pcobra/cobra/transpilers/registry.py"
GOLDEN_DIR = ROOT / "tests/integration/transpilers/golden"
BENCHMARKS_DIR = ROOT / "scripts/benchmarks"

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
from pcobra.cobra.transpilers.reverse.policy import (
    REVERSE_SCOPE_MODULES,
    normalize_reverse_language,
)
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
    "node_modules/",
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
    ROOT / "docs/experimental/plan_nuevas_funcionalidades_hololang.md",
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
        "BEST_EFFORT_RUNTIME_TARGETS",
        "NO_RUNTIME_TARGETS",
    }
)
POLICY_LITERAL_PREFIX_NAMES = frozenset(
    {
        "CLI_OFFICIAL_RUNTIME_TARGETS",
        "CLI_TRANSPILATION_ONLY_TARGETS",
    }
)

EXPECTED_OFFICIAL_TARGETS = (
    "python",
    "rust",
    "javascript",
    "wasm",
    "go",
    "cpp",
    "java",
    "asm",
)
EXPECTED_REVERSE_SCOPE_LANGUAGES = ("python", "javascript", "java")
EXPECTED_TRANSPILER_MODULES = (
    "to_python.py",
    "to_rust.py",
    "to_js.py",
    "to_wasm.py",
    "to_go.py",
    "to_cpp.py",
    "to_java.py",
    "to_asm.py",
)
EXPECTED_REVERSE_MODULES = (
    "from_python.py",
    "from_js.py",
    "from_java.py",
)
EXPECTED_TRANSPILER_REGISTRY = {
    "python": ("pcobra.cobra.transpilers.transpiler.to_python", "TranspiladorPython"),
    "rust": ("pcobra.cobra.transpilers.transpiler.to_rust", "TranspiladorRust"),
    "javascript": ("pcobra.cobra.transpilers.transpiler.to_js", "TranspiladorJavaScript"),
    "wasm": ("pcobra.cobra.transpilers.transpiler.to_wasm", "TranspiladorWasm"),
    "go": ("pcobra.cobra.transpilers.transpiler.to_go", "TranspiladorGo"),
    "cpp": ("pcobra.cobra.transpilers.transpiler.to_cpp", "TranspiladorCPP"),
    "java": ("pcobra.cobra.transpilers.transpiler.to_java", "TranspiladorJava"),
    "asm": ("pcobra.cobra.transpilers.transpiler.to_asm", "TranspiladorASM"),
}
EXPECTED_REVERSE_SCOPE_MODULES = {
    "python": "pcobra.cobra.transpilers.reverse.from_python",
    "javascript": "pcobra.cobra.transpilers.reverse.from_js",
    "java": "pcobra.cobra.transpilers.reverse.from_java",
}
EXPECTED_REVERSE_SCOPE_CLASS_NAMES = {
    "python": "ReverseFromPython",
    "javascript": "ReverseFromJS",
    "java": "ReverseFromJava",
}
TARGETED_ARTIFACT_SCAN_ROOTS = (
    TRANSPILER_DIR,
    REVERSE_DIR,
    GOLDEN_DIR,
    BENCHMARKS_DIR,
    *PUBLIC_TEXT_PATHS,
)
TARGETED_ARTIFACT_FILENAME_ALLOWLIST = {
    "tests/integration/transpilers/golden": {
        f"{target}.golden" for target in EXPECTED_OFFICIAL_TARGETS
    },
}
FORBIDDEN_PUBLIC_ALIAS_TOKENS = frozenset(NON_CANONICAL_PUBLIC_NAMES)

PUBLIC_POLICY_LIST_PATTERNS: dict[str, tuple[re.Pattern[str], str]] = {
    "official_targets": (
        re.compile(r"targets oficiales de transpilación", re.IGNORECASE),
        "targets oficiales de transpilación",
    ),
    "official_targets_available": (
        re.compile(r"lenguajes destino disponibles", re.IGNORECASE),
        "lenguajes destino disponibles",
    ),
    "official_targets_accepted_names": (
        re.compile(r"official backend names are accepted", re.IGNORECASE),
        "official backend names are accepted",
    ),
    "official_runtime_targets": (
        re.compile(r"targets con runtime oficial", re.IGNORECASE),
        "targets con runtime oficial",
    ),
    "reverse_scope_languages": (
        re.compile(r"or[ií]genes de transpilaci[oó]n inversa", re.IGNORECASE),
        "orígenes reverse oficiales",
    ),
    "reverse_scope_languages_available": (
        re.compile(r"lenguajes de origen disponibles", re.IGNORECASE),
        "lenguajes de origen disponibles",
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
    "official_standard_library_targets": (
        re.compile(r"soporte oficial mantenido de `corelibs`/`standard_library` en runtime", re.IGNORECASE),
        "soporte oficial mantenido de corelibs/standard_library en runtime",
    ),
    "advanced_holobit_runtime_targets": (
        re.compile(r"soporte holobit avanzado mantenido por el proyecto", re.IGNORECASE),
        "soporte Holobit avanzado mantenido por el proyecto",
    ),
    "sdk_compatible_targets": (
        re.compile(r"compatibilidad sdk completa", re.IGNORECASE),
        "compatibilidad SDK completa",
    ),
}


ARCHIVE_LINK_REQUIRED_MARKERS = (
    "experimental",
    "histórico",
    "historico",
    "interno",
    "interna",
    "internal",
    "fuera de política",
    "fuera de politica",
    "sin vigencia",
)

LEGACY_PUBLIC_OPTION_PATTERNS: dict[str, re.Pattern[str]] = {
    "--a": re.compile(r"(?<![\w-])(--a)(?![\w-])"),
    "--to": re.compile(r"(?<![\w-])(--to)(?![\w-])"),
    "--lenguaje": re.compile(r"(?<![\w-])(--lenguaje)(?![\w-])"),
}

PUBLIC_NON_OFFICIAL_LABELLED_PATTERNS: dict[str, tuple[re.Pattern[str], tuple[str, ...]]] = {
    "hololang-public-context": (
        re.compile(
            r"(?=.*\bhololang\b)(?=.*\b(?:target|targets|destino|destinos|backend|backends|salida|output)\b)",
            re.IGNORECASE,
        ),
        ("interno", "interna", "internal", "experimental", "ir"),
    ),
    "llvm-public-context": (
        re.compile(
            r"(?=.*\bllvm\b)(?=.*\b(?:target|targets|destino|destinos|backend|backends|salida|output)\b)",
            re.IGNORECASE,
        ),
        ("experimental", "fuera de política", "fuera de politica", "interno", "interna", "internal"),
    ),
    "latex-public-context": (
        re.compile(
            r"(?=.*\blatex\b)(?=.*\b(?:target|targets|destino|destinos|backend|backends|origen|orígenes|origenes|salida|output)\b)",
            re.IGNORECASE,
        ),
        ("experimental", "fuera de política", "fuera de politica", "interno", "interna", "internal"),
    ),
    "reverse-wasm-public-context": (
        re.compile(
            r"\b(?:reverse\s+(?:desde|from)\s+(?:wasm|webassembly)|(?:wasm|webassembly)\s+reverse)\b",
            re.IGNORECASE,
        ),
        ("experimental", "retirado", "histórico", "historico", "fuera de política", "fuera de politica"),
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


def _literal_string_collection(node: ast.AST | None) -> tuple[str, ...] | None:
    if not isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return None

    values: list[str] = []
    for element in node.elts:
        if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
            return None
        values.append(element.value)
    return tuple(values)


def _literal_string_dict(
    node: ast.AST | None,
) -> dict[str, str | tuple[str, ...]] | None:
    if not isinstance(node, ast.Dict):
        return None

    literal: dict[str, str | tuple[str, ...]] = {}
    for key, value in zip(node.keys, node.values):
        if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
            return None
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            literal[key.value] = value.value
            continue
        collection = _literal_string_collection(value)
        if collection is None:
            return None
        literal[key.value] = collection
    return literal


def _read_assignment_literal(path: Path, name: str) -> ast.AST | None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == name:
                return node.value
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return node.value
    return None


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
    best_effort_runtime_targets: tuple[str, ...],
    no_runtime_targets: tuple[str, ...],
    verification_targets: tuple[str, ...],
) -> tuple[str, ...] | None:
    if name == "SUPPORTED_TARGETS" or name == "OFFICIAL_TARGETS":
        return official_targets
    if name in {"OFFICIAL_RUNTIME_TARGETS", "DOCKER_EXECUTABLE_TARGETS"}:
        return official_runtime_targets
    if name == "TRANSPILATION_ONLY_TARGETS":
        return transpilation_only_targets
    if name == "BEST_EFFORT_RUNTIME_TARGETS":
        return best_effort_runtime_targets
    if name == "NO_RUNTIME_TARGETS":
        return no_runtime_targets
    if name == "VERIFICATION_EXECUTABLE_TARGETS":
        return verification_targets
    return None


def validate_transpiler_modules(official: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    if tuple(official) != EXPECTED_OFFICIAL_TARGETS:
        errors.append(
            "OFFICIAL_TARGETS no coincide con la whitelist mantenida por CI -> "
            f"{tuple(official)} (esperado: {EXPECTED_OFFICIAL_TARGETS})"
        )
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

    exact_modules = tuple(sorted(path.name for path in TRANSPILER_DIR.glob("to_*.py")))
    if exact_modules != tuple(sorted(EXPECTED_TRANSPILER_MODULES)):
        errors.append(
            "src/pcobra/cobra/transpilers/transpiler: el árbol to_*.py debe contener "
            f"exactamente {list(EXPECTED_TRANSPILER_MODULES)} -> encontrados={list(exact_modules)}"
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
    expected = tuple((*tier1_targets, *tier2_targets))

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

    if tuple(ORIGIN_CHOICES) != tuple(reverse_scope_languages):
        errors.append(
            "transpilar-inverso: ORIGIN_CHOICES no coincide con REVERSE_SCOPE_LANGUAGES "
            f"-> origen={ORIGIN_CHOICES}, reverse={tuple(reverse_scope_languages)}"
        )

    reverse_registry = tuple(REVERSE_TRANSPILERS.keys())
    missing = sorted(set(reverse_scope_languages) - set(reverse_registry))
    extras = sorted(set(reverse_registry) - set(reverse_scope_languages))
    if missing:
        errors.append(
            "transpilar-inverso: REVERSE_TRANSPILERS no cubre todos los orígenes "
            f"canónicos -> faltan {', '.join(missing)}"
        )
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
    official_standard_library_targets: tuple[str, ...],
    advanced_holobit_runtime_targets: tuple[str, ...],
    sdk_compatible_targets: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    allowed_names = set(official_targets) | set(official_runtime_targets) | set(
        reverse_scope_languages
    ) | set(transpilation_only_targets) | set(verification_targets) | set(
        official_standard_library_targets
    ) | set(advanced_holobit_runtime_targets) | set(sdk_compatible_targets)
    expected_values = {
        "official_targets": set(official_targets),
        "official_targets_available": set(official_targets),
        "official_targets_accepted_names": set(official_targets),
        "official_runtime_targets": set(official_runtime_targets),
        "official_runtime_targets_alt": set(official_runtime_targets),
        "reverse_scope_languages": set(reverse_scope_languages),
        "reverse_scope_languages_available": set(reverse_scope_languages),
        "transpilation_only_targets": set(transpilation_only_targets),
        "verification_targets": set(verification_targets),
        "official_standard_library_targets": set(official_standard_library_targets),
        "advanced_holobit_runtime_targets": set(advanced_holobit_runtime_targets),
        "sdk_compatible_targets": set(sdk_compatible_targets),
    }

    for path in PUBLIC_TEXT_PATHS:
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
        lowered = content.lower()
        if "escalar" in lowered or "mover" in lowered:
            has_python_only_disclaimer = (
                "solo python" in lowered
                or "runtime python" in lowered
            )
            has_out_of_contract_disclaimer = (
                "no forman parte del contrato" in lowered
                or "no forman parte de esta matriz" in lowered
                or "fuera de alcance del contrato" in lowered
            )
            if not (has_python_only_disclaimer and has_out_of_contract_disclaimer):
                errors.append(
                    f"{rel}: `escalar`/`mover` no deben mezclarse con el contrato Holobit sin aclarar que son helpers solo-Python fuera de la matriz"
                )

    return errors


def validate_module_file_scope(
    official_targets: tuple[str, ...],
    reverse_scope_languages: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    if tuple(reverse_scope_languages) != EXPECTED_REVERSE_SCOPE_LANGUAGES:
        errors.append(
            "REVERSE_SCOPE_LANGUAGES no coincide con la whitelist mantenida por CI -> "
            f"{tuple(reverse_scope_languages)} (esperado: {EXPECTED_REVERSE_SCOPE_LANGUAGES})"
        )
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

    reverse_dir_modules = sorted(path.name for path in REVERSE_DIR.glob("from_*.py"))
    expected_reverse_dir_modules = sorted(
        Path(module_name.rsplit(".", 1)[-1] + ".py").name
        for module_name in REVERSE_SCOPE_MODULES.values()
    )
    if reverse_dir_modules != expected_reverse_dir_modules:
        errors.append(
            "src/pcobra/cobra/transpilers/reverse: los módulos from_*.py no coinciden "
            "exactamente con la política reverse oficial -> "
            f"encontrados={reverse_dir_modules}, esperados={expected_reverse_dir_modules}"
        )
    if tuple(reverse_dir_modules) != tuple(sorted(EXPECTED_REVERSE_MODULES)):
        errors.append(
            "src/pcobra/cobra/transpilers/reverse: el árbol from_*.py debe contener "
            f"exactamente {list(EXPECTED_REVERSE_MODULES)} -> encontrados={reverse_dir_modules}"
        )

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


def validate_registry_tables() -> list[str]:
    errors: list[str] = []

    registry_literal = _literal_string_dict(
        _read_assignment_literal(TRANSPILER_REGISTRY_PATH, "TRANSPILER_CLASS_PATHS")
    )
    expected_registry_literal = {
        key: value for key, value in EXPECTED_TRANSPILER_REGISTRY.items()
    }
    if registry_literal != expected_registry_literal:
        errors.append(
            "src/pcobra/cobra/transpilers/registry.py: TRANSPILER_CLASS_PATHS debe coincidir "
            f"exactamente con el registro oficial -> encontrado={registry_literal}, "
            f"esperado={expected_registry_literal}"
        )

    reverse_languages = _literal_string_collection(
        _read_assignment_literal(REVERSE_POLICY_PATH, "REVERSE_SCOPE_LANGUAGES")
    )
    if reverse_languages != EXPECTED_REVERSE_SCOPE_LANGUAGES:
        errors.append(
            "src/pcobra/cobra/transpilers/reverse/policy.py: REVERSE_SCOPE_LANGUAGES debe "
            f"coincidir exactamente con la whitelist reverse -> encontrado={reverse_languages}, "
            f"esperado={EXPECTED_REVERSE_SCOPE_LANGUAGES}"
        )

    reverse_modules = _literal_string_dict(
        _read_assignment_literal(REVERSE_POLICY_PATH, "REVERSE_SCOPE_MODULES")
    )
    if reverse_modules != EXPECTED_REVERSE_SCOPE_MODULES:
        errors.append(
            "src/pcobra/cobra/transpilers/reverse/policy.py: REVERSE_SCOPE_MODULES debe "
            f"coincidir exactamente con el registro reverse oficial -> encontrado={reverse_modules}, "
            f"esperado={EXPECTED_REVERSE_SCOPE_MODULES}"
        )

    reverse_class_names = _literal_string_dict(
        _read_assignment_literal(REVERSE_POLICY_PATH, "REVERSE_SCOPE_CLASS_NAMES")
    )
    if reverse_class_names != EXPECTED_REVERSE_SCOPE_CLASS_NAMES:
        errors.append(
            "src/pcobra/cobra/transpilers/reverse/policy.py: REVERSE_SCOPE_CLASS_NAMES debe "
            f"coincidir exactamente con el registro reverse oficial -> encontrado={reverse_class_names}, "
            f"esperado={EXPECTED_REVERSE_SCOPE_CLASS_NAMES}"
        )

    return errors


def validate_python_policy_literals(
    official_targets: tuple[str, ...],
    *,
    official_runtime_targets: tuple[str, ...],
    transpilation_only_targets: tuple[str, ...],
    best_effort_runtime_targets: tuple[str, ...],
    no_runtime_targets: tuple[str, ...],
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
                    best_effort_runtime_targets=best_effort_runtime_targets,
                    no_runtime_targets=no_runtime_targets,
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


def _collect_python_transpiler_imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set()

    imports: set[str] = set()
    prefixes = (
        "cobra.transpilers.transpiler.to_",
        "pcobra.cobra.transpilers.transpiler.to_",
    )
    for node in ast.walk(tree):
        modules: list[str] = []
        if isinstance(node, ast.ImportFrom) and node.module:
            modules = [node.module]
        elif isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]

        for module in modules:
            for prefix in prefixes:
                if module.startswith(prefix):
                    imports.add(module.removeprefix(prefix))
    return imports


def validate_targeted_artifact_roots(
    official_targets: tuple[str, ...],
    reverse_scope_languages: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    allowed_transpiler_imports = set(official_targets)
    allowed_reverse_imports = set(reverse_scope_languages)
    transpiler_alias_map = {"js": "javascript"}
    reverse_alias_map = {"js": "javascript"}

    for root in TARGETED_ARTIFACT_SCAN_ROOTS:
        if not root.exists():
            continue
        files = (root,) if root.is_file() else tuple(
            candidate for candidate in sorted(root.rglob("*")) if candidate.is_file()
        )
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            if _is_generated_or_binary(path):
                continue

            for prefix, allowed in TARGETED_ARTIFACT_FILENAME_ALLOWLIST.items():
                if rel.startswith(prefix + "/") and path.name not in allowed:
                    errors.append(
                        f"{rel}: artefacto no oficial en árbol vigilado -> {path.name} "
                        f"(permitidos: {sorted(allowed)})"
                    )

            if path.suffix == ".py":
                for imported in sorted(_collect_python_transpiler_imports(path)):
                    canonical = transpiler_alias_map.get(imported, imported)
                    if canonical not in allowed_transpiler_imports:
                        errors.append(
                            f"{rel}: import a transpilador fuera del conjunto oficial -> to_{imported}"
                        )
                for imported in sorted(_collect_python_reverse_imports(path)):
                    canonical = reverse_alias_map.get(imported, normalize_reverse_language(imported))
                    if canonical not in allowed_reverse_imports:
                        errors.append(
                            f"{rel}: import reverse fuera del conjunto reverse oficial -> from_{imported}"
                        )

            lowered_name_parts = [part.lower() for part in path.parts]
            if any(part in {"golden", "fixtures", "benchmarks"} for part in lowered_name_parts):
                stem_tokens = re.split(r"[^a-z0-9+_-]+", path.stem.lower())
                for alias in sorted(FORBIDDEN_PUBLIC_ALIAS_TOKENS):
                    if alias in stem_tokens:
                        errors.append(
                            f"{rel}: artefacto asociado a alias público no permitido -> {alias}"
                        )

    return errors


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
                if rel in PUBLIC_TEXT_PATH_STRS:
                    for option_name, pattern in LEGACY_PUBLIC_OPTION_PATTERNS.items():
                        match = pattern.search(line)
                        if match:
                            errors.append(
                                f"{rel}:{line_no}: opción CLI pública obsoleta/no canónica -> {option_name}"
                            )

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
                    if ("docs/experimental/" in line or "docs/historico/" in line) and not any(
                        marker in lowered for marker in ARCHIVE_LINK_REQUIRED_MARKERS
                    ):
                        errors.append(
                            f"{rel}:{line_no}: enlace ambiguo a docs/experimental o docs/historico sin etiqueta visible"
                        )

                    for pattern_name, (pattern, markers) in PUBLIC_NON_OFFICIAL_LABELLED_PATTERNS.items():
                        if not pattern.search(line):
                            continue
                        if pattern_name == "hololang-public-context" and any(
                            marker in lowered
                            for marker in ("no expone", "no es", "no describe", "pipeline interno")
                        ):
                            continue
                        if not any(marker in lowered for marker in markers):
                            errors.append(
                                f"{rel}:{line_no}: referencia pública ambigua fuera de política -> {pattern_name}"
                            )

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
    best_effort_runtime_targets = policy["best_effort_runtime_targets"]
    no_runtime_targets = policy["no_runtime_targets"]
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
            official_standard_library_targets=tuple(policy["official_standard_library_targets"]),
            advanced_holobit_runtime_targets=tuple(policy["advanced_holobit_runtime_targets"]),
            sdk_compatible_targets=tuple(policy["sdk_compatible_targets"]),
        )
    )
    errors.extend(validate_holobit_public_contract())
    errors.extend(validate_module_file_scope(official_targets, reverse_scope))
    errors.extend(validate_registry_tables())
    errors.extend(
        validate_python_policy_literals(
            official_targets,
            official_runtime_targets=official_runtime_targets,
            transpilation_only_targets=transpilation_only_targets,
            best_effort_runtime_targets=best_effort_runtime_targets,
            no_runtime_targets=no_runtime_targets,
            verification_targets=verification_targets,
        )
    )
    errors.extend(validate_scan_roots(official_targets, reverse_scope))
    errors.extend(validate_targeted_artifact_roots(official_targets, reverse_scope))

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
