#!/usr/bin/env python3
"""Validaciones anti-regresión para targets oficiales y aliases legacy.

Checks:
1) OFFICIAL_TARGETS (targets.py) == claves de TRANSPILERS (compile_cmd.py).
2) No existen módulos to_*.py fuera de targets oficiales (considerando aliases legacy).
3) Detección textual de aliases legacy en rutas públicas de CLI/docs de usuario.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS_FILE = ROOT / "src/pcobra/cobra/transpilers/targets.py"
COMPILE_CMD_FILE = ROOT / "src/pcobra/cobra/cli/commands/compile_cmd.py"
TRANSPILER_DIR = ROOT / "src/pcobra/cobra/transpilers/transpiler"

PUBLIC_TEXT_PATHS = (
    ROOT / "src/pcobra/cobra/cli/commands/compile_cmd.py",
    ROOT / "src/pcobra/cobra/cli/target_policies.py",
    ROOT / "README.md",
    ROOT / "docs/config_cli.md",
    ROOT / "docs/lenguajes_soportados.rst",
    ROOT / "docs/frontend/index.rst",
    ROOT / "docs/frontend/avances.rst",
    ROOT / "docs/frontend/ejemplos.rst",
)

LEGACY_ALIAS_ALLOWLIST: dict[str, tuple[re.Pattern[str], ...]] = {
    "docs/lenguajes_soportados.rst": (
        re.compile(r"alias:\s*``js``", re.IGNORECASE),
    ),
    "src/pcobra/cobra/cli/target_policies.py": (
        re.compile(r'"javascript"\s*:\s*"js"', re.IGNORECASE),
    ),
}


def _literal_eval(node: ast.AST):
    return ast.literal_eval(node)


def read_official_targets_and_aliases() -> tuple[tuple[str, ...], dict[str, str]]:
    tree = ast.parse(TARGETS_FILE.read_text(encoding="utf-8"), filename=str(TARGETS_FILE))
    values: dict[str, object] = {}

    for stmt in tree.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            name = stmt.target.id
            if stmt.value is None:
                continue
            try:
                values[name] = _literal_eval(stmt.value)
            except Exception:
                pass
        elif isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    try:
                        values[target.id] = _literal_eval(stmt.value)
                    except Exception:
                        pass

    official = values.get("OFFICIAL_TARGETS")
    if not isinstance(official, tuple):
        # fallback: TIER1 + TIER2
        tier1 = values.get("TIER1_TARGETS", ())
        tier2 = values.get("TIER2_TARGETS", ())
        official = tuple(tier1) + tuple(tier2)

    legacy_aliases = values.get("LEGACY_TARGET_ALIASES", {})
    if not isinstance(legacy_aliases, dict):
        legacy_aliases = {}

    return tuple(str(t) for t in official), {str(k): str(v) for k, v in legacy_aliases.items()}


def read_transpiler_registry_keys() -> set[str]:
    tree = ast.parse(COMPILE_CMD_FILE.read_text(encoding="utf-8"), filename=str(COMPILE_CMD_FILE))
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == "TRANSPILERS" and isinstance(stmt.value, ast.Dict):
                    keys = set()
                    for key in stmt.value.keys:
                        if isinstance(key, ast.Constant) and isinstance(key.value, str):
                            keys.add(key.value)
                    return keys
    raise RuntimeError("No se pudo leer TRANSPILERS desde compile_cmd.py")


def validate_transpiler_modules(official: tuple[str, ...], legacy_aliases: dict[str, str]) -> list[str]:
    errors: list[str] = []
    to_files = sorted(TRANSPILER_DIR.glob("to_*.py"))

    normalized_allowed = set(official)
    for alias, canonical in legacy_aliases.items():
        if canonical in normalized_allowed:
            normalized_allowed.add(alias)

    for file_path in to_files:
        suffix = file_path.stem[3:]  # remove to_
        canonical = legacy_aliases.get(suffix, suffix)
        if canonical not in official:
            errors.append(
                f"{file_path.relative_to(ROOT)}: módulo fuera de OFFICIAL_TARGETS -> to_{suffix}.py"
            )

    return errors


def validate_no_legacy_aliases_in_public_paths(legacy_aliases: dict[str, str]) -> list[str]:
    errors: list[str] = []
    # Check textual aliases used as target values in CLI/docs.
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
                m = pat.search(line)
                if not m:
                    continue
                if any(ap.search(line) for ap in allow_patterns):
                    continue
                errors.append(f"{rel}:{line_no}: alias legacy en ruta pública -> {m.group(1)}")

    return errors


def main() -> int:
    errors: list[str] = []

    official_targets, legacy_aliases = read_official_targets_and_aliases()
    transpilers = read_transpiler_registry_keys()

    missing_in_registry = sorted(set(official_targets) - transpilers)
    extra_in_registry = sorted(transpilers - set(official_targets))

    if missing_in_registry or extra_in_registry:
        errors.append("Desalineación OFFICIAL_TARGETS vs TRANSPILERS:")
        if missing_in_registry:
            errors.append(f"  - faltan en TRANSPILERS: {', '.join(missing_in_registry)}")
        if extra_in_registry:
            errors.append(f"  - sobran en TRANSPILERS: {', '.join(extra_in_registry)}")

    errors.extend(validate_transpiler_modules(official_targets, legacy_aliases))
    errors.extend(validate_no_legacy_aliases_in_public_paths(legacy_aliases))

    if errors:
        print("❌ Validación anti-regresión de targets: FALLÓ", file=sys.stderr)
        for err in errors:
            print(f" - {err}", file=sys.stderr)
        return 1

    print("✅ Validación anti-regresión de targets: OK")
    print(f"   OFFICIAL_TARGETS: {', '.join(official_targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
