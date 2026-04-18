#!/usr/bin/env python3
"""Genera docs/MANUAL_COBRA.rst a partir de docs/MANUAL_COBRA.md."""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "MANUAL_COBRA.md"
TARGET = ROOT / "docs" / "MANUAL_COBRA.rst"

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")


def _convert_inline(text: str) -> str:
    text = INLINE_CODE_RE.sub(r"``\1``", text)
    text = LINK_RE.sub(r"`\1 <\2>`_", text)
    return text


def _heading_level(line: str) -> int:
    stripped = line.lstrip()
    return len(stripped) - len(stripped.lstrip("#"))


def _heading_underline(level: int, text: str) -> str:
    if level <= 1:
        return "=" * len(text)
    if level == 2:
        return "-" * len(text)
    return "~" * len(text)


def convert_markdown_to_rst(markdown_text: str) -> str:
    out: list[str] = [
        ".. Archivo autogenerado, no editar manualmente.",
        ".. Fuente canónica: docs/MANUAL_COBRA.md",
        "",
    ]

    in_code = False
    code_lines: list[str] = []
    in_note = False

    for raw in markdown_text.splitlines():
        line = raw.rstrip("\n")

        if line.startswith("```"):
            if not in_code:
                in_code = True
                code_lines = []
            else:
                out.append("::")
                out.append("")
                out.extend(f"   {code}" for code in code_lines)
                out.append("")
                in_code = False
                code_lines = []
            continue

        if in_code:
            code_lines.append(line)
            continue

        if line.startswith(">"):
            content = line[1:].lstrip()
            if not in_note:
                out.append(".. note::")
                in_note = True
            if content:
                out.append(f"   {_convert_inline(content)}")
            else:
                out.append("")
            continue

        if in_note:
            out.append("")
            in_note = False

        if not line.strip():
            out.append("")
            continue

        level = _heading_level(line)
        if level:
            title = _convert_inline(line[level:].strip())
            out.append(title)
            out.append(_heading_underline(level, title))
            continue

        if line.startswith("- "):
            out.append(f"- {_convert_inline(line[2:])}")
            continue

        if line[:2].isdigit() and line[1:3] in {". ", ") "}:
            out.append(_convert_inline(line))
            continue

        out.append(_convert_inline(line))

    if in_note:
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    markdown_text = SOURCE.read_text(encoding="utf-8")
    rst_text = convert_markdown_to_rst(markdown_text)
    TARGET.write_text(rst_text, encoding="utf-8")
    print(f"[manual-ref] Generado: {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
