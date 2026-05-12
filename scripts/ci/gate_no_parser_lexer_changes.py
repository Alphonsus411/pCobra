#!/usr/bin/env python3
"""Gate de CI: bloquea cambios en lexer/parser canónicos."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

CANONICAL_SYNTAX_PATHS = (
    Path("src/pcobra/cobra/core/lexer.py"),
    Path("src/pcobra/cobra/core/parser.py"),
)


def _parse_name_status(output: str) -> list[Path]:
    changed: list[Path] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) < 2:
            continue

        status = parts[0]
        paths = parts[1:]

        if status.startswith(("R", "C")) and len(paths) >= 2:
            changed.append(Path(paths[0]))
            changed.append(Path(paths[1]))
            continue

        changed.append(Path(paths[0]))

    return changed


def _git_changed_files(base: str, head: str) -> list[Path]:
    cmd = ["git", "diff", "--name-status", f"{base}...{head}"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff falló")
    return _parse_name_status(result.stdout)


def _find_blocked_paths(changed: list[Path]) -> list[Path]:
    blocked = []
    blocked_set = {p.as_posix() for p in CANONICAL_SYNTAX_PATHS}
    for path in changed:
        if path.as_posix() in blocked_set:
            blocked.append(path)
    return blocked


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Falla si se detectan cambios en lexer/parser canónicos "
            "dentro del alcance del trabajo actual"
        )
    )
    parser.add_argument("--base", help="SHA/rama base para diff", default=None)
    parser.add_argument("--head", help="SHA/rama head para diff", default="HEAD")
    parser.add_argument(
        "--changed-file",
        action="append",
        default=[],
        help="Archivo modificado (puede repetirse). Si se usa, omite git diff.",
    )
    args = parser.parse_args()

    if args.changed_file:
        changed_files = [Path(p) for p in args.changed_file]
    else:
        base = args.base or "HEAD~1"
        try:
            changed_files = _git_changed_files(base, args.head)
        except RuntimeError as exc:
            print(f"[gate-no-parser-lexer] error: {exc}", file=sys.stderr)
            return 2

    blocked = _find_blocked_paths(changed_files)
    if blocked:
        print("[gate-no-parser-lexer] Se detectaron cambios sintácticos bloqueados:")
        for path in blocked:
            print(f" - {path.as_posix()}")
        print(
            "Si necesitas extender módulos/core runtime, evita cambios de sintaxis "
            "(lexer/parser) en este alcance."
        )
        return 1

    print("[gate-no-parser-lexer] OK: sin cambios en lexer/parser canónicos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
