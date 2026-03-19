#!/usr/bin/env python3
"""Detecta usos de aliases legacy de targets en rutas públicas y tests."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ("tests", "docs", "examples/hello_world")
FILE_EXTS = {".py", ".md", ".rst", ".txt", ".yml", ".yaml"}
PUBLIC_DOC_GLOBS = (
    "README.md",
    "docs/*.md",
    "docs/*.rst",
    "docs/frontend/*.rst",
)
LEGACY_ALIASES = {
    "js": "javascript",
    "ensamblador": "asm",
}

# Allowlist explícita para casos en los que el alias legacy se prueba/documenta
# intencionalmente (compatibilidad retroactiva).
ALLOWLIST = {
    "docs/targets_policy.md",
    "tests/unit/test_cli_target_aliases.py",
    "tests/unit/test_target_policies.py",
    "tests/unit/test_reverse_scope_docs_consistency.py",
    "tests/unit/test_cli_transpilar_inverso_cmd.py",
    "tests/unit/test_cli_official_language_restrictions.py",
    "tests/unit/test_compile_cmd_target_choices_aliases.py",
    "tests/unit/test_compile_backend_registration.py",
    "tests/unit/test_mod_validator.py",
    "tests/unit/test_verify_cmd.py",
    "tests/unit/test_official_targets_consistency.py",
    "tests/unit/test_reverse_transpilers_registry.py",
    "tests/performance/test_transpile_time.py",
    "tests/utils/runtime.py",
    "tests/integration/test_runtime_js.py",
    "tests/unit/test_option_statement.py",
    "tests/unit/test_tipos_colecciones.py",
    "tests/unit/test_smoke_transpilation_official_targets.py",
    "tests/unit/test_transpiler_backend_regression.py",
    "tests/unit/test_cli_compilar_tipos.py",
    "tests/unit/test_cobra_module_map.py",
    "tests/unit/test_enum.py",
    "tests/unit/test_cli_commands_extra.py",
    "tests/unit/test_to_js4.py",
    "tests/unit/test_module_map.py",
    "tests/unit/test_validar_dependencias.py",
    "tests/unit/test_pcobra_config.py",
    "tests/unit/test_pcobra_module_map.py",
    "tests/unit/test_to_js3.py",
    "tests/unit/test_corelibs.py",
    "tests/unit/test_option_pattern_roundtrip.py",
    "tests/unit/test_to_js.py",
    "tests/unit/test_module_map_errors.py",
    "tests/unit/test_benchmarks2_cmd.py",
    "tests/integration/test_transpile_semantics.py",
    "tests/integration/test_cross_backend_output.py",
    "tests/integration/test_end_to_end.py",
}

PATTERNS = [
    re.compile(r'([\'"])(js|ensamblador)\1', re.IGNORECASE),
    re.compile(r"``(js|ensamblador)``", re.IGNORECASE),
    re.compile(
        r"\b(?:--(?:tipo|tipos|to|destino|contenedor|lenguajes|backend|origen)(?:=|\s+))(js|ensamblador)\b",
        re.IGNORECASE,
    ),
]


def iter_files():
    for folder in SCAN_DIRS:
        base = ROOT / folder
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in FILE_EXTS:
                yield path


def iter_public_doc_paths() -> set[Path]:
    paths: set[Path] = set()
    for pattern in PUBLIC_DOC_GLOBS:
        paths.update(path for path in ROOT.glob(pattern) if path.is_file())
    return paths


def main() -> int:
    errors: list[str] = []
    public_doc_paths = iter_public_doc_paths()
    for path in iter_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel in ALLOWLIST:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line_no, line in enumerate(text.splitlines(), start=1):
            line_for_check = line.replace('.js', '')
            for pattern in PATTERNS:
                match = pattern.search(line_for_check)
                if not match:
                    continue
                alias = match.group(2) if match.lastindex and match.lastindex >= 2 else match.group(1)
                context = (
                    'ruta pública de documentación'
                    if path in public_doc_paths
                    else 'ruta escaneada'
                )
                canonical = LEGACY_ALIASES.get(alias.lower(), '?')
                errors.append(
                    f"{rel}:{line_no}: uso legacy detectado en {context} -> {alias} (usar {canonical})"
                )
                break

    if errors:
        print("Se detectaron aliases legacy fuera de la allowlist:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("OK: no se detectaron aliases legacy fuera de la allowlist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
