#!/usr/bin/env python3
"""Detecta usos de aliases legacy de lenguajes en tests/documentación."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ("tests", "docs", "examples/hello_world")
FILE_EXTS = {".py", ".md", ".rst", ".txt", ".yml", ".yaml"}

# Allowlist explícita para casos en los que el alias legacy se prueba/documenta
# intencionalmente (compatibilidad retroactiva).
ALLOWLIST = {
    "docs/targets_policy.md",
    "docs/lenguajes_soportados.rst",
    "tests/unit/test_cli_target_aliases.py",
    "tests/unit/test_target_policies.py",
    "tests/unit/test_reverse_scope_docs_consistency.py",
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
    "docs/frontend/design_patterns.rst",
    "tests/integration/test_transpile_semantics.py",
    "tests/integration/test_cross_backend_output.py",
    "tests/integration/test_end_to_end.py",
}

PATTERNS = [
    re.compile(r"(['\"])js\1"),
    re.compile(r"--(?:tipo|tipos|to|destino|contenedor|lenguajes)(?:=|\s+[^\n]*\s)js\b"),
]


def iter_files():
    for folder in SCAN_DIRS:
        base = ROOT / folder
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in FILE_EXTS:
                yield path


def main() -> int:
    errors: list[str] = []
    for path in iter_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel in ALLOWLIST:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        for i, line in enumerate(lines, start=1):
            if ".js" in line:
                line_for_check = line.replace(".js", "")
            else:
                line_for_check = line
            if any(p.search(line_for_check) for p in PATTERNS):
                errors.append(f"{rel}:{i}: uso legacy detectado -> {line.strip()}")

    if errors:
        print("Se detectaron aliases legacy ('js') fuera de la allowlist:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("OK: no se detectaron aliases legacy fuera de la allowlist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
