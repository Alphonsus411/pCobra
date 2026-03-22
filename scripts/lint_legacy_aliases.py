#!/usr/bin/env python3
"""Detecta aliases legacy y extras retirados en código productivo, docs públicas y ayudas de CLI."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.targets_policy_common import NON_CANONICAL_PUBLIC_NAMES

SCAN_PATHS = [
    ROOT / "pyproject.toml",
    ROOT / "README.md",
    ROOT / "docs",
    ROOT / "examples",
    ROOT / "extensions/vscode/README.md",
    ROOT / "extensions/vscode/snippets",
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

TEXT_EXTS = {".py", ".md", ".rst", ".toml", ".yaml", ".yml", ".json", ".txt"}
IGNORED_PATH_PREFIXES = (
    "docs/experimental/",
    "docs/frontend/api/",
    "docs/historico/",
)

LEGACY_ALIAS_TERMS = tuple(sorted(NON_CANONICAL_PUBLIC_NAMES))
LEGACY_ALIAS_GROUP = "|".join(re.escape(term) for term in LEGACY_ALIAS_TERMS)
LEGACY_OPTION_GROUP = r"--a"

CONFIG_ALIAS_PATTERNS = [
    re.compile(rf"(?m)^\s*(?:{LEGACY_ALIAS_GROUP})\s*="),
    re.compile(rf'''(?m)["'](?:{LEGACY_ALIAS_GROUP})["']\s*:'''),
]

PUBLIC_ALIAS_PATTERNS = [
    re.compile(
        rf"(?i)(?:targets?|backends?|lenguajes?|destinos?)\s+(?:can[oó]nicos?|oficiales)[^\n]*\b({LEGACY_ALIAS_GROUP})\b"
    ),
    re.compile(rf"(?i)lista can[oó]nica[^\n]*\b({LEGACY_ALIAS_GROUP})\b"),
]

CLI_HELP_OR_SNIPPET_PATTERNS = [
    re.compile(
        rf"(?i)(?:cobra\s+(?:compilar|transpilar-inverso)|--(?:tipo|tipos|backend|destino|origen|lenguajes|contenedor)|lenguajes?\s+(?:destino|de origen)\s+disponibles|accepted\s+names|runtime\s+oficial|targets?\s+oficiales)[^\n]*\b({LEGACY_ALIAS_GROUP})\b"
    ),
    re.compile(
        rf"(?i)(?:aliases?\s+legacy|alias(?:es)?\s+retirad[oa]s?|abreviaturas?\s+hist[oó]ricas?)[^\n]*\b({LEGACY_ALIAS_GROUP})\b"
    ),
    re.compile(rf"(?i)(?:cobra\s+(?:compilar|transpilar-inverso)|--(?:tipo|tipos|backend|destino|origen))([^\n]*\s{LEGACY_OPTION_GROUP})(?![\w-])"),
]

GENERAL_PUBLIC_ALIAS_TOKEN_PATTERNS = [
    re.compile(rf"(?i)(?<![\w.+/-])({LEGACY_ALIAS_GROUP})(?![\w.+/-])"),
]

LEGACY_ALIAS_LINE_ALLOWLIST = {
    "tests/unit/test_mod_validator.py": (re.compile(r'"js"\s*:'),),
}


def _strip_known_extensions(line: str) -> str:
    return (
        line.replace(".js", "")
        .replace(".mjs", "")
        .replace(".cjs", "")
        .replace(".cpp", "")
        .replace(".wasm", "")
        .replace("Node.js", "Node")
    )


def _is_public_text(rel: str) -> bool:
    return rel.startswith(("README.md", "docs/", "examples/", "extensions/"))


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
        is_public = _is_public_text(rel)

        for line_no, line in enumerate(text.splitlines(), start=1):
            line_for_check = _strip_known_extensions(line)
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
                else:
                    for pattern in CLI_HELP_OR_SNIPPET_PATTERNS:
                        match = pattern.search(line_for_check)
                        if not match:
                            continue
                        token = match.group(1).strip()
                        errors.append(
                            f"{rel}:{line_no}: alias legacy detectado en ayuda/snippet/mensaje público -> {token}"
                        )
                        break
                    else:
                        if not is_public:
                            continue
                        for pattern in GENERAL_PUBLIC_ALIAS_TOKEN_PATTERNS:
                            match = pattern.search(line_for_check)
                            if not match:
                                continue
                            errors.append(
                                f"{rel}:{line_no}: alias público fuera de política detectado -> {match.group(1).strip()}"
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
