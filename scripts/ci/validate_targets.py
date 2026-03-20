#!/usr/bin/env python3
"""Validaciones anti-regresión para targets oficiales.

Checks:
1) Igualdad exacta entre ``OFFICIAL_TARGETS`` y las claves efectivas de ``TRANSPILERS``.
2) No existen módulos ``to_*.py`` fuera de los 8 targets oficiales.
3) Detección textual de aliases legacy en rutas públicas de CLI/docs de usuario.
4) ``transpilar-inverso`` expone únicamente orígenes reverse canónicos y destinos
   dentro de ``OFFICIAL_TARGETS``.
5) La documentación pública y los ejemplos no mencionan módulos reverse borrados,
   extras no vigentes ni ejemplos CLI fuera de política, salvo que estén marcados
   explícitamente como históricos/no vigentes.
"""

from __future__ import annotations

import sys
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
TRANSPILER_DIR = ROOT / "src/pcobra/cobra/transpilers/transpiler"

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
from scripts.targets_policy_common import (
    LEGACY_ALIAS_ALLOWLIST,
    PUBLIC_TEXT_PATHS,
    build_legacy_alias_patterns,
    read_target_policy,
)


def read_transpiler_registry_keys() -> tuple[str, ...]:
    return tuple(TRANSPILERS.keys())



def validate_transpiler_modules(official: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    allowed_suffixes = {"javascript" if target == "javascript" else target for target in official}
    alias_suffix_map = {"js": "javascript"}

    for file_path in sorted(TRANSPILER_DIR.glob("to_*.py")):
        suffix = file_path.stem.removeprefix("to_")
        canonical = alias_suffix_map.get(suffix, suffix)
        if canonical not in official:
            errors.append(
                f"{file_path.relative_to(ROOT)}: módulo fuera de OFFICIAL_TARGETS -> to_{suffix}.py"
            )
            continue
        if suffix not in allowed_suffixes and suffix not in alias_suffix_map:
            errors.append(
                f"{file_path.relative_to(ROOT)}: sufijo no canónico para target oficial -> to_{suffix}.py"
            )

    return errors



def validate_no_legacy_aliases_in_public_paths(legacy_aliases: dict[str, str]) -> list[str]:
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
                errors.append(f"{rel}:{line_no}: alias legacy en ruta pública -> {match.group(1)}")

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


DOCUMENTATION_SCAN_ROOTS = (
    ROOT / "README.md",
    ROOT / "docs",
    ROOT / "examples",
)

DOCUMENTATION_PATH_EXCLUDE_PARTS = (
    "docs/notebooks/",
)

DOCUMENTATION_ALLOWED_HISTORICAL_PARTS = (
    "docs/historico/",
)

REMOVED_REVERSE_MODULE_PATTERNS = (
    "from_c.py",
    "from_cpp.py",
    "from_go.py",
    "from_rust.py",
    "from_wasm.py",
    "from_asm.py",
)

HISTORICAL_MARKERS = ("histórico", "historico", "no vigente")


def _iter_documentation_files() -> tuple[Path, ...]:
    files: list[Path] = []
    for path in DOCUMENTATION_SCAN_ROOTS:
        if path.is_file():
            files.append(path)
            continue
        files.extend(candidate for candidate in path.rglob("*") if candidate.is_file())
    return tuple(sorted(files))


def _is_historical_context(rel: str, line: str) -> bool:
    rel_lower = rel.lower()
    line_lower = line.lower()
    return any(part in rel_lower for part in DOCUMENTATION_ALLOWED_HISTORICAL_PARTS) or any(
        marker in line_lower for marker in HISTORICAL_MARKERS
    )


def validate_documentation_policy(
    official_targets: tuple[str, ...],
    reverse_scope_languages: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    official_target_set = set(official_targets)
    reverse_scope_set = set(reverse_scope_languages)
    option_pattern = re.compile(r"--(?P<kind>origen|destino)(?:=|\s+)(?P<value>[a-zA-Z0-9_-]+)")

    for path in _iter_documentation_files():
        rel = path.relative_to(ROOT).as_posix()
        if any(part in rel for part in DOCUMENTATION_PATH_EXCLUDE_PARTS):
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if _is_historical_context(rel, line):
                continue

            lowered = line.lower()

            for removed_module in REMOVED_REVERSE_MODULE_PATTERNS:
                if removed_module in lowered:
                    errors.append(
                        f"{rel}:{line_no}: referencia documental a módulo reverse retirado -> {removed_module}"
                    )

            if "reverse-wasm" in lowered:
                errors.append(
                    f"{rel}:{line_no}: referencia documental a extra reverse fuera del alcance vigente -> reverse-wasm"
                )

            if "transpilar-inverso" not in lowered:
                continue

            for match in option_pattern.finditer(line):
                kind = match.group("kind")
                value = match.group("value").strip().lower()
                if kind == "origen" and value not in reverse_scope_set:
                    errors.append(
                        f"{rel}:{line_no}: origen reverse fuera de REVERSE_SCOPE_LANGUAGES -> {value}"
                    )
                if kind == "destino" and value not in official_target_set:
                    errors.append(
                        f"{rel}:{line_no}: destino reverse fuera de OFFICIAL_TARGETS -> {value}"
                    )

    return errors



def main() -> int:
    errors: list[str] = []

    policy = read_target_policy()
    official_targets = policy["official_targets"]
    legacy_aliases = policy["legacy_aliases"]
    transpilers = read_transpiler_registry_keys()

    if transpilers != official_targets:
        missing_in_registry = sorted(set(official_targets) - set(transpilers))
        extra_in_registry = sorted(set(transpilers) - set(official_targets))
        errors.append("Desalineación OFFICIAL_TARGETS vs TRANSPILERS:")
        errors.append(f"  - OFFICIAL_TARGETS: {', '.join(official_targets)}")
        errors.append(f"  - TRANSPILERS: {', '.join(transpilers)}")
        if missing_in_registry:
            errors.append(f"  - faltan en TRANSPILERS: {', '.join(missing_in_registry)}")
        if extra_in_registry:
            errors.append(f"  - sobran en TRANSPILERS: {', '.join(extra_in_registry)}")

    errors.extend(validate_transpiler_modules(official_targets))
    errors.extend(validate_no_legacy_aliases_in_public_paths(legacy_aliases))
    errors.extend(validate_reverse_cli_contract(official_targets, tuple(REVERSE_SCOPE_LANGUAGES)))
    errors.extend(validate_documentation_policy(official_targets, tuple(REVERSE_SCOPE_LANGUAGES)))

    if errors:
        print("❌ Validación anti-regresión de targets: FALLÓ", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)
        return 1

    print("✅ Validación anti-regresión de targets: OK")
    print(f"   Tier 1: {', '.join(policy['tier1_targets'])}")
    print(f"   Tier 2: {', '.join(policy['tier2_targets'])}")
    print(f"   OFFICIAL_TARGETS: {', '.join(official_targets)}")
    print(f"   TRANSPILERS: {', '.join(transpilers)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
