#!/usr/bin/env python3
"""Valida que los workflows no referencien targets/backends fuera de política."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.targets_policy_common import read_target_policy

WORKFLOWS_DIR = ROOT / ".github" / "workflows"

RETIRED_REFERENCE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?<![\w/-])hololang(?![\w/-])", re.IGNORECASE), "backend retirado 'hololang'"),
    (
        re.compile(r"(?<![\w/-])reverse[ -]wasm(?![\w/-])", re.IGNORECASE),
        "pipeline retirado 'reverse wasm'",
    ),
    (
        re.compile(
            r"(?i)(backend|target|pipeline|transpiler)[^\n]{0,48}\bllvm\b|\bllvm\b[^\n]{0,48}(backend|target|pipeline|transpiler)"
        ),
        "referencia de target/pipeline retirado 'llvm'",
    ),
    (
        re.compile(
            r"(?i)(backend|target|pipeline|transpiler)[^\n]{0,48}\blatex\b|\blatex\b[^\n]{0,48}(backend|target|pipeline|transpiler)"
        ),
        "referencia de target/pipeline retirado 'latex'",
    ),
)

TARGET_KEY_PATTERN = re.compile(r"^\s*(?:target|targets|backend|backends)\s*:\s*(.+?)\s*$", re.IGNORECASE)
LIST_ITEM_PATTERN = re.compile(r"^\s*-\s*([a-zA-Z0-9_+\- ]+)\s*$")


def _normalize_target(value: str) -> str:
    return value.strip().strip("'\"").lower()


def _extract_inline_items(raw_value: str) -> tuple[str, ...]:
    value = raw_value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1]
        if not inner.strip():
            return tuple()
        return tuple(_normalize_target(item) for item in inner.split(",") if item.strip())
    return tuple()


def validate_workflow(path: Path, allowed_targets: set[str]) -> list[str]:
    errors: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()

    full_text = "\n".join(lines)
    for pattern, label in RETIRED_REFERENCE_PATTERNS:
        for match in pattern.finditer(full_text):
            line_no = full_text.count("\n", 0, match.start()) + 1
            errors.append(
                f"{path.relative_to(ROOT).as_posix()}:{line_no}: {label}"
            )

    for idx, line in enumerate(lines, start=1):
        match = TARGET_KEY_PATTERN.match(line)
        if not match:
            continue
        inline_items = _extract_inline_items(match.group(1))
        for item in inline_items:
            if item and item not in allowed_targets:
                errors.append(
                    f"{path.relative_to(ROOT).as_posix()}:{idx}: target/backend no permitido en lista inline -> '{item}'"
                )

        if inline_items:
            continue
        cursor = idx
        while cursor < len(lines):
            candidate = lines[cursor]
            list_match = LIST_ITEM_PATTERN.match(candidate)
            if not list_match:
                break
            item = _normalize_target(list_match.group(1))
            if item and item not in allowed_targets:
                errors.append(
                    f"{path.relative_to(ROOT).as_posix()}:{cursor + 1}: target/backend no permitido en lista -> '{item}'"
                )
            cursor += 1

    return errors


def main() -> int:
    policy = read_target_policy()
    allowed_targets = set(policy["official_targets"])

    errors: list[str] = []
    for workflow in sorted(WORKFLOWS_DIR.glob("*.yml")):
        errors.extend(validate_workflow(workflow, allowed_targets))

    if errors:
        print("❌ Validación de política de targets en workflows: FALLÓ", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("✅ Validación de política de targets en workflows: OK")
    print(f"   Targets permitidos: {', '.join(sorted(allowed_targets))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
