#!/usr/bin/env python3
"""Regenera docs de targets y falla si quedan cambios sin commitear."""

from __future__ import annotations

import subprocess
import sys

GENERATION_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("python", "scripts/generate_target_policy_docs.py"),
    ("python", "scripts/generar_matriz_transpiladores.py"),
)

WATCHED_PATHS: tuple[str, ...] = (
    "docs/targets_policy.md",
    "docs/matriz_transpiladores.md",
    "docs/matriz_transpiladores.csv",
    "docs/_generated",
    "README.md",
    "docs/README.en.md",
)


def _run(command: tuple[str, ...]) -> None:
    print(f"[targets-docs] Ejecutando: {' '.join(command)}")
    subprocess.run(command, check=True)


def _diff_has_changes() -> bool:
    tracked_result = subprocess.run(
        ("git", "diff", "--quiet", "--", *WATCHED_PATHS),
        check=False,
    )
    if tracked_result.returncode != 0:
        return True

    untracked_result = subprocess.run(
        ("git", "status", "--porcelain", "--untracked-files=all", "--", *WATCHED_PATHS),
        check=False,
        capture_output=True,
        text=True,
    )
    return bool(untracked_result.stdout.strip())


def _print_diff() -> None:
    subprocess.run(("git", "--no-pager", "diff", "--", *WATCHED_PATHS), check=False)
    subprocess.run(
        ("git", "status", "--short", "--untracked-files=all", "--", *WATCHED_PATHS),
        check=False,
    )


def main() -> int:
    for command in GENERATION_COMMANDS:
        _run(command)

    if _diff_has_changes():
        print(
            "[targets-docs] ERROR: hay diferencias sin commitear tras regenerar docs de targets."
        )
        _print_diff()
        print(
            "[targets-docs] Ejecuta los scripts de generación y commitea el resultado esperado."
        )
        return 1

    print("[targets-docs] OK: artefactos de targets sincronizados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
