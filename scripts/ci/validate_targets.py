#!/usr/bin/env python3
"""Validaciones anti-regresión para targets oficiales.

Checks:
1) Igualdad exacta entre ``OFFICIAL_TARGETS`` y las claves efectivas de ``TRANSPILERS``.
2) No existen módulos ``to_*.py`` fuera de los 8 targets oficiales.
3) Detección textual de aliases legacy en rutas públicas de CLI/docs de usuario.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
TRANSPILER_DIR = ROOT / "src/pcobra/cobra/transpilers/transpiler"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pcobra.cobra.cli.commands.compile_cmd import TRANSPILERS
from pcobra.cobra.transpilers.targets import LEGACY_TARGET_ALIASES, OFFICIAL_TARGETS

PUBLIC_TEXT_PATHS = (
    ROOT / "src/pcobra/cobra/cli/commands/compile_cmd.py",
    ROOT / "src/pcobra/cobra/cli/target_policies.py",
    ROOT / "src/pcobra/cobra/cli/commands/benchmarks_cmd.py",
    ROOT / "README.md",
    ROOT / "docs/config_cli.md",
    ROOT / "docs/lenguajes_soportados.rst",
    ROOT / "docs/frontend/index.rst",
    ROOT / "docs/frontend/avances.rst",
    ROOT / "docs/frontend/ejemplos.rst",
)

LEGACY_ALIAS_ALLOWLIST: dict[str, tuple[re.Pattern[str], ...]] = {}



def read_official_targets_and_aliases() -> tuple[tuple[str, ...], dict[str, str]]:
    return tuple(OFFICIAL_TARGETS), dict(LEGACY_TARGET_ALIASES)



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
    alias_group = "|".join(re.escape(alias) for alias in sorted(legacy_aliases))
    if not alias_group:
        return errors

    patterns = (
        re.compile(rf"\b(?:--(?:tipo|tipos|backend|origen|destino)\s+|--(?:tipo|tipos|backend|origen|destino)=)({alias_group})\b", re.IGNORECASE),
        re.compile(rf"['\"]({alias_group})['\"]", re.IGNORECASE),
        re.compile(rf"``({alias_group})``", re.IGNORECASE),
    )

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



def main() -> int:
    errors: list[str] = []

    official_targets, legacy_aliases = read_official_targets_and_aliases()
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

    if errors:
        print("❌ Validación anti-regresión de targets: FALLÓ", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)
        return 1

    print("✅ Validación anti-regresión de targets: OK")
    print(f"   OFFICIAL_TARGETS: {', '.join(official_targets)}")
    print(f"   TRANSPILERS: {', '.join(transpilers)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
