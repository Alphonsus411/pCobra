#!/usr/bin/env python3
"""Genera snippets públicos derivados de la política canónica de targets.

Este script evita que README, docs y ejemplos mantengan listas manuales
separadas de la fuente de verdad en:
- ``src/pcobra/cobra/transpilers/targets.py``
- ``src/pcobra/cobra/transpilers/registry.py``
- ``src/pcobra/cobra/cli/target_policies.py``
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pcobra.cobra.cli.target_policies import (  # noqa: E402
    BEST_EFFORT_RUNTIME_TARGETS,
    NO_RUNTIME_TARGETS,
    OFFICIAL_RUNTIME_TARGETS,
    OFFICIAL_STANDARD_LIBRARY_TARGETS,
    SDK_COMPATIBLE_TARGETS,
    VERIFICATION_EXECUTABLE_TARGETS,
    render_public_policy_summary,
    render_reverse_scope_summary,
)
from pcobra.cobra.transpilers.compatibility_matrix import (  # noqa: E402
    BACKEND_COMPATIBILITY,
)
from pcobra.cobra.transpilers.registry import official_transpiler_targets  # noqa: E402
from pcobra.cobra.transpilers.reverse import REVERSE_SCOPE_LANGUAGES  # noqa: E402
from pcobra.cobra.transpilers.target_utils import (  # noqa: E402
    build_tier_summary_lines,
    format_target_name,
    format_target_sequence,
    official_target_rows,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS, TIER1_TARGETS, TIER2_TARGETS  # noqa: E402

GENERATED_DIR = ROOT / "docs" / "_generated"
MARKER_START = "<!-- BEGIN GENERATED TARGET POLICY SUMMARY -->"
MARKER_END = "<!-- END GENERATED TARGET POLICY SUMMARY -->"
EN_MARKER_START = "<!-- BEGIN GENERATED TARGET POLICY SUMMARY EN -->"
EN_MARKER_END = "<!-- END GENERATED TARGET POLICY SUMMARY EN -->"


def _policy_summary_md() -> str:
    return "\n".join(
        [
            render_public_policy_summary(markup="markdown"),
            render_reverse_scope_summary(tuple(REVERSE_SCOPE_LANGUAGES), markup="markdown"),
            "",
            "Tiers oficiales de soporte de backends:",
            "",
            *[f"- {line}" for line in build_tier_summary_lines(markup="markdown")],
        ]
    ).strip() + "\n"


def _policy_summary_en_md() -> str:
    return "\n".join(
        [
            "- **Official transpilation targets**: " + format_target_sequence(OFFICIAL_TARGETS, markup="markdown") + ".",
            "- **Targets with official verifiable runtime**: " + format_target_sequence(OFFICIAL_RUNTIME_TARGETS, markup="markdown") + ".",
            "- **Targets with explicit executable CLI verification**: " + format_target_sequence(VERIFICATION_EXECUTABLE_TARGETS, markup="markdown") + ".",
            "- **Targets with best-effort runtime**: " + format_target_sequence(BEST_EFFORT_RUNTIME_TARGETS, markup="markdown") + ".",
            "- **Targets with maintained `corelibs`/`standard_library` runtime support**: " + format_target_sequence(OFFICIAL_STANDARD_LIBRARY_TARGETS, markup="markdown") + ".",
            "- **Targets with project-maintained Holobit adapter**: " + format_target_sequence(OFFICIAL_RUNTIME_TARGETS, markup="markdown") + ".",
            "- **Full SDK compatibility**: " + format_target_sequence(SDK_COMPATIBLE_TARGETS, markup="markdown") + ".",
            "- **Transpilation-only targets**: " + format_target_sequence(NO_RUNTIME_TARGETS, markup="markdown") + ".",
            "- **Reverse transpilation input origins**: " + format_target_sequence(REVERSE_SCOPE_LANGUAGES, markup="markdown") + ".",
            "",
            "Official backend support tiers:",
            "",
            "- **Tier 1**: " + format_target_sequence(TIER1_TARGETS, markup="markdown") + ".",
            "- **Tier 2**: " + format_target_sequence(TIER2_TARGETS, markup="markdown") + ".",
        ]
    ).strip() + "\n"


def _official_targets_table_rst() -> str:
    lines = [
        ".. list-table:: Estado de los backends oficiales",
        "   :header-rows: 1",
        "",
        "   * - Lenguaje",
        "     - Identificador CLI",
        "     - Tier",
        "     - Runtime público",
        "     - Holobit público",
        "     - SDK real",
    ]
    for row in official_target_rows():
        backend = row["target"]
        holobit_status = (
            "full"
            if backend in SDK_COMPATIBLE_TARGETS
            else "adaptador mantenido (partial)"
            if backend in OFFICIAL_RUNTIME_TARGETS
            else "partial"
        )
        runtime_status = (
            "oficial verificable"
            if backend in OFFICIAL_RUNTIME_TARGETS
            else "best-effort no público"
            if backend in BEST_EFFORT_RUNTIME_TARGETS
            else "solo transpilación"
        )
        sdk_status = "completa" if backend in SDK_COMPATIBLE_TARGETS else "parcial"
        lines.extend(
            [
                f"   * - {row['label']}",
                f"     - ``{backend}``",
                f"     - {row['tier']}",
                f"     - {runtime_status}",
                f"     - {holobit_status}",
                f"     - {sdk_status}",
            ]
        )
    return "\n".join(lines) + "\n"


def _runtime_capability_matrix_rst() -> str:
    lines = [
        ".. list-table:: Diferencia entre transpilación, runtime, Holobit y SDK",
        "   :header-rows: 1",
        "",
        "   * - Backend",
        "     - Tier",
        "     - Runtime oficial verificable",
        "     - Runtime best-effort no público",
        "     - Holobit mantenido por el proyecto",
        "     - ``corelibs``/``standard_library`` oficiales en runtime",
        "     - Compatibilidad SDK completa",
    ]
    for backend in OFFICIAL_TARGETS:
        tier = BACKEND_COMPATIBILITY[backend]["tier"].replace("tier", "Tier ")
        lines.extend(
            [
                f"   * - ``{backend}``",
                f"     - {tier}",
                f"     - {'Sí' if backend in OFFICIAL_RUNTIME_TARGETS else 'No'}",
                f"     - {'Sí' if backend in BEST_EFFORT_RUNTIME_TARGETS else 'No'}",
                f"     - {'Sí' if backend in OFFICIAL_RUNTIME_TARGETS else 'No'}",
                f"     - {'Sí' if backend in OFFICIAL_STANDARD_LIBRARY_TARGETS else 'No'}",
                f"     - {'Sí' if backend in SDK_COMPATIBLE_TARGETS else 'No'}",
            ]
        )
    return "\n".join(lines) + "\n"


def _reverse_scope_table_rst() -> str:
    lines = [
        ".. list-table:: Lenguajes de entrada reverse",
        "   :header-rows: 1",
        "",
        "   * - Lenguaje",
        "     - Identificador CLI",
        "     - Estado",
    ]
    for language in REVERSE_SCOPE_LANGUAGES:
        lines.extend(
            [
                f"   * - {language.title() if language != 'javascript' else 'JavaScript'}",
                f"     - ``{language}``",
                "     - Experimental controlado",
            ]
        )
    return "\n".join(lines) + "\n"


def _cli_backend_examples_rst() -> str:
    lines = [".. code-block:: bash", ""]
    for backend in official_transpiler_targets():
        lines.append(f"   cobra compilar programa.co --backend {backend}")
    return "\n".join(lines) + "\n"


def _policy_summary_rst() -> str:
    return "\n".join(
        [
            render_public_policy_summary(markup="rst"),
            render_reverse_scope_summary(tuple(REVERSE_SCOPE_LANGUAGES), markup="rst"),
            "",
            "Tiers oficiales de soporte de backends:",
            "",
            *[f"- {line}" for line in build_tier_summary_lines(markup="rst")],
        ]
    ).strip() + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _inject_between_markers(text: str, *, start: str, end: str, body: str) -> str:
    if start not in text or end not in text:
        raise RuntimeError(f"No se encontraron marcadores requeridos: {start} / {end}")
    prefix, remainder = text.split(start, 1)
    _, suffix = remainder.split(end, 1)
    return prefix + start + "\n" + body.rstrip() + "\n" + end + suffix


def sync_readme_blocks() -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    updated = _inject_between_markers(text, start=MARKER_START, end=MARKER_END, body=_policy_summary_md())
    readme.write_text(updated, encoding="utf-8")

    readme_en = ROOT / "docs" / "README.en.md"
    text_en = readme_en.read_text(encoding="utf-8")
    updated_en = _inject_between_markers(text_en, start=EN_MARKER_START, end=EN_MARKER_END, body=_policy_summary_en_md())
    readme_en.write_text(updated_en, encoding="utf-8")


def generate() -> None:
    _write(GENERATED_DIR / "target_policy_summary.rst", _policy_summary_rst())
    _write(GENERATED_DIR / "official_targets_table.rst", _official_targets_table_rst())
    _write(GENERATED_DIR / "runtime_capability_matrix.rst", _runtime_capability_matrix_rst())
    _write(GENERATED_DIR / "reverse_scope_table.rst", _reverse_scope_table_rst())
    _write(GENERATED_DIR / "cli_backend_examples.rst", _cli_backend_examples_rst())
    _write(GENERATED_DIR / "target_policy_summary.md", _policy_summary_md())
    sync_readme_blocks()


if __name__ == "__main__":
    generate()
