#!/usr/bin/env python3
"""Verifica el contrato: control-flow no abre scopes ni copia entornos."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INTERPRETER_PATH = ROOT / "src" / "pcobra" / "core" / "interpreter.py"

FORBIDDEN_PATTERNS = (
    "env.copy(",
    "dict(env.values)",
)


def _extract_method_source(source: str, method_name: str) -> str:
    marker = f"def {method_name}("
    start = source.find(marker)
    if start < 0:
        raise RuntimeError(f"No se encontró el método {method_name} en interpreter.py")

    end = len(source)
    next_def = source.find("\n    def ", start + len(marker))
    if next_def > start:
        end = next_def
    return source[start:end]


def find_violations(root: Path = ROOT) -> list[str]:
    source = (root / "src" / "pcobra" / "core" / "interpreter.py").read_text(
        encoding="utf-8"
    )
    while_source = _extract_method_source(source, "ejecutar_mientras")
    if_source = _extract_method_source(source, "ejecutar_condicional")

    violations: list[str] = []
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in while_source:
            violations.append(
                f"src/pcobra/core/interpreter.py: patrón prohibido `{pattern}` dentro de `ejecutar_mientras`"
            )
        if pattern in if_source:
            violations.append(
                f"src/pcobra/core/interpreter.py: patrón prohibido `{pattern}` dentro de `ejecutar_condicional`"
            )

    if "self.contextos.append(" in while_source:
        violations.append(
            "src/pcobra/core/interpreter.py: `ejecutar_mientras` no debe crear scopes por iteración (`self.contextos.append` detectado)"
        )
    return violations


def main() -> int:
    violations = find_violations(ROOT)
    if not violations:
        print(
            "OK: control-flow cumple contrato (sin copias de entorno ni scopes nuevos en while)."
        )
        return 0

    for violation in violations:
        print(violation)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
