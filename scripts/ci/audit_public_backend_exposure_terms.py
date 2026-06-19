#!/usr/bin/env python3
"""Audita que alias/backends retirados no reaparezcan en superficies públicas.

La regla protege registros públicos de transpiladores, choices de CLI/GUI y
la documentación de usuario no histórica. Las menciones se permiten solo en
contextos explícitamente históricos, pruebas de rechazo o shims legacy.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_PUBLIC_TERMS = ("go", "cpp", "java", "wasm", "asm", "py", "js", "node", "golang", "jvm")
OFFICIAL_PUBLIC_BACKENDS = ("python", "javascript", "rust")
_TERM_RE = re.compile(r"(?<![\w.+/-])(" + "|".join(map(re.escape, FORBIDDEN_PUBLIC_TERMS)) + r")(?![\w.+/-])", re.IGNORECASE)

PUBLIC_REGISTRY_FILES = (
    Path("src/pcobra/cobra/transpilers/registry.py"),
    Path("src/pcobra/cobra/transpilers/targets.py"),
    Path("src/pcobra/cobra/config/transpile_targets.py"),
)
ACTIVE_RUNTIME_SNAPSHOT = Path("src/pcobra/cobra/transpilers/runtime_api_parity_snapshot.json")
CHOICE_ROOTS = (
    Path("src/pcobra/cobra/cli"),
    Path("src/pcobra/gui"),
    Path("src/pcobra/cobra/gui"),
)
DOC_ROOTS = (Path("README.md"), Path("docs"))

HISTORICAL_DOC_PARTS = {"historico", "compatibility", "ADR", "issues", "proposals", "informes"}
HISTORICAL_DOC_FILES = {
    Path("docs/migracion_targets_retirados.md"),
    Path("docs/language_equivalence_matrix.md"),
    Path("docs/architecture/adr-unified-3-backends.md"),
    Path("docs/architecture/cobra_unified_architecture_execution_plan.md"),
}
REJECTION_TEST_PREFIXES = (Path("tests"),)
LEGACY_SHIM_PREFIXES = (Path("src/cobra"),)

CHOICE_MARKERS = ("choices", "choice", "target_cli_choices", "gui_target_choices", "dropdown", "option(")
HISTORICAL_MARKERS = ("histórico", "historico", "legacy", "retirad", "migración", "migracion", "depreca")
DOC_EXPOSURE_MARKERS = ("backend", "target", "transpil", "lenguaje", "lenguajes", "destino", "origen", "runtime oficial", "tiers", "tier ", "disponible")


@dataclass(frozen=True)
class Violation:
    path: Path
    line_no: int
    term: str
    scope: str
    line: str

    def format(self) -> str:
        return f"{self.path}:{self.line_no}: {self.scope}: término público prohibido {self.term!r}: {self.line.strip()}"


def _is_under(path: Path, prefix: Path) -> bool:
    return path == prefix or path.parts[: len(prefix.parts)] == prefix.parts


def _is_rejection_test(path: Path) -> bool:
    return any(_is_under(path, prefix) for prefix in REJECTION_TEST_PREFIXES) and "rechaz" in path.read_text(encoding="utf-8", errors="ignore").lower()


def _is_legacy_shim(path: Path) -> bool:
    return any(_is_under(path, prefix) for prefix in LEGACY_SHIM_PREFIXES)


def _is_historical_doc(path: Path, text: str) -> bool:
    if path in HISTORICAL_DOC_FILES:
        return True
    if any(part in HISTORICAL_DOC_PARTS for part in path.parts):
        return True
    head = "\n".join(text.lower().splitlines()[:30])
    return any(marker in head for marker in HISTORICAL_MARKERS)


def _text_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".rst", ".txt"}]


def _scan_lines(path: Path, scope: str, *, require_choice_marker: bool = False, root: Path = ROOT) -> list[Violation]:
    display_path = path.relative_to(root) if path.is_absolute() and path.is_relative_to(root) else path
    text = path.read_text(encoding="utf-8", errors="ignore")
    if _is_rejection_test(display_path) or _is_legacy_shim(display_path):
        return []
    if scope == "documentación pública" and _is_historical_doc(display_path, text):
        return []

    violations: list[Violation] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if require_choice_marker and not any(marker in lowered for marker in CHOICE_MARKERS):
            continue
        if scope == "documentación pública":
            if any(marker in lowered for marker in HISTORICAL_MARKERS):
                continue
            if not any(marker in lowered for marker in DOC_EXPOSURE_MARKERS):
                continue
        for match in _TERM_RE.finditer(line):
            violations.append(Violation(display_path, line_no, match.group(1), scope, line))
    return violations


def find_violations(root: Path = ROOT) -> list[Violation]:
    violations: list[Violation] = []

    for rel in PUBLIC_REGISTRY_FILES:
        path = root / rel
        if path.exists():
            violations.extend(_scan_lines(path, "registro público de transpiladores", root=root))

    for choice_root in CHOICE_ROOTS:
        absolute = root / choice_root
        if not absolute.exists():
            continue
        for path in sorted(absolute.rglob("*.py")):
            rel = path.relative_to(root)
            violations.extend(_scan_lines(path, "choices públicos CLI/GUI", require_choice_marker=True, root=root))

    for doc_root in DOC_ROOTS:
        absolute = root / doc_root
        if not absolute.exists():
            continue
        for path in sorted(_text_files(absolute)):
            rel = path.relative_to(root)
            violations.extend(_scan_lines(path, "documentación pública", root=root))

    return violations


def _audit_active_runtime_snapshot(root: Path = ROOT) -> list[Violation]:
    """Verifica que el snapshot activo no publique backends retirados."""
    path = root / ACTIVE_RUNTIME_SNAPSHOT
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    backend_runtime_api = data.get("backend_runtime_api")
    if not isinstance(backend_runtime_api, dict):
        return [
            Violation(
                ACTIVE_RUNTIME_SNAPSHOT,
                1,
                "backend_runtime_api",
                "snapshot activo de runtime",
                "backend_runtime_api debe ser un objeto JSON",
            )
        ]

    violations: list[Violation] = []
    active_keys = tuple(backend_runtime_api)
    if active_keys != OFFICIAL_PUBLIC_BACKENDS:
        legacy_keys = [key for key in active_keys if key in FORBIDDEN_PUBLIC_TERMS]
        term = ",".join(legacy_keys) if legacy_keys else ",".join(active_keys)
        violations.append(
            Violation(
                ACTIVE_RUNTIME_SNAPSHOT,
                1,
                term,
                "snapshot activo de runtime",
                "backend_runtime_api debe exponer exactamente python, javascript y rust; "
                "las entradas legacy deben vivir en historical_backend_runtime_api",
            )
        )
    return violations


def main() -> int:
    violations = find_violations(ROOT)
    violations.extend(_audit_active_runtime_snapshot(ROOT))
    if violations:
        print("❌ Auditor de exposiciones públicas de backends/alias retirados: FALLÓ", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation.format()}", file=sys.stderr)
        print(
            "Regla: go/cpp/java/wasm/asm/py/js/node/golang/jvm solo pueden aparecer "
            "en documentos históricos explícitos, pruebas de rechazo o shims legacy autorizados.",
            file=sys.stderr,
        )
        return 1
    print("✅ Auditor de exposiciones públicas de backends/alias retirados: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
