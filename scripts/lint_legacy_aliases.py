#!/usr/bin/env python3
"""Detecta aliases legacy y extras retirados en código productivo, docs públicas y fixtures de configuración."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCAN_PATHS = [
    ROOT / "pyproject.toml",
    ROOT / "README.md",
    ROOT / "docs/config_cli.md",
    ROOT / "docs/guia_basica.md",
    ROOT / "examples/README.md",
    ROOT / "examples/hello_world/README.md",
    ROOT / "docs/frontend",
    ROOT / "pcobra.toml",
    ROOT / "cobra.toml",
    ROOT / "src/pcobra/cobra/transpilers/targets.py",
    ROOT / "src/pcobra/cobra/cli/target_policies.py",
    ROOT / "src/pcobra/cobra/cli/cli.py",
    ROOT / "src/pcobra/cobra/transpilers/module_map.py",
    ROOT / "src/pcobra/cobra/cli/commands/compile_cmd.py",
    ROOT / "src/pcobra/cobra/cli/commands/benchmarks2_cmd.py",
    ROOT / "src/pcobra/cobra/transpilers/reverse/policy.py",
    ROOT / "src/pcobra/cobra/semantico/mod_validator.py",
    ROOT / "src/pcobra/cobra/semantico/cobra_mod_schema.yaml",
    ROOT / "src/pcobra/core/sandbox.py",
    ROOT / "tests/unit/test_module_map.py",
    ROOT / "tests/unit/test_pcobra_module_map.py",
    ROOT / "tests/unit/test_cobra_module_map.py",
    ROOT / "tests/unit/test_mod_validator.py",
    ROOT / "tests/unit/test_smoke_transpilation_official_targets.py",
    ROOT / "tests/unit/test_pcobra_config.py",
    ROOT / "tests/unit/test_validar_dependencias.py",
]

CONFIG_ALIAS_PATTERNS = [
    re.compile(r"(?m)^\s*(?:js|ensamblador)\s*="),
    re.compile(r'''(?m)["'](?:js|ensamblador)["']\s*:'''),
    re.compile(r"(?m)\b(?:reverse-wasm|wabt|sexpdata)\b"),
]

TEXT_EXTS = {".py", ".md", ".rst", ".toml", ".yaml", ".yml"}
PUBLIC_ALIAS_PATTERNS = [
    re.compile(r"(?i)(?:targets?|backends?|lenguajes?|destinos?)\s+(?:can[oó]nicos?|oficiales)[^\n]*\b(js|ensamblador)\b"),
    re.compile(r"(?i)lista can[oó]nica[^\n]*\b(js|ensamblador)\b"),
]

IGNORED_PATH_PREFIXES = ("docs/frontend/api/",)
LEGACY_ALIAS_LINE_ALLOWLIST = {
    "tests/unit/test_mod_validator.py": (re.compile(r'"js"\s*:'),),
}


def iter_files():
    for base in SCAN_PATHS:
        if not base.exists():
            continue
        if base.is_file():
            yield base
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix in TEXT_EXTS:
                rel = path.relative_to(ROOT).as_posix()
                if rel.startswith(IGNORED_PATH_PREFIXES):
                    continue
                yield path


def main() -> int:
    errors: list[str] = []
    for path in iter_files():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        allowlisted = LEGACY_ALIAS_LINE_ALLOWLIST.get(rel, ())
        for line_no, line in enumerate(text.splitlines(), start=1):
            line_for_check = line.replace('.js', '').replace('.mjs', '').replace('.cjs', '')
            if any(pattern.search(line_for_check) for pattern in allowlisted):
                continue
            for pattern in CONFIG_ALIAS_PATTERNS:
                match = pattern.search(line_for_check)
                if not match:
                    continue
                errors.append(
                    f"{rel}:{line_no}: referencia legacy/retirada detectada -> {match.group(0).strip()}"
                )
                break
            else:
                for pattern in PUBLIC_ALIAS_PATTERNS:
                    match = pattern.search(line_for_check)
                    if not match:
                        continue
                    errors.append(
                        f"{rel}:{line_no}: alias público no canónico presentado como oficial -> {match.group(1).strip()}"
                    )
                    break

    if errors:
        print("Se detectaron aliases legacy o extras retirados:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("OK: no se detectaron aliases legacy ni extras retirados en rutas vigiladas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
