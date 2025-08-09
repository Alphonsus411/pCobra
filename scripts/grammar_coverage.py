#!/usr/bin/env python
"""Calculate grammar rule coverage for sample files.

This script loads ``docs/gramatica.ebnf`` using ``lark.Lark`` and parses
all ``.co`` files found in the ``examples/`` and ``src/tests/``
directories. It records which grammar rules are used when parsing and
computes the percentage of rules that were exercised. If the coverage is
below a configurable threshold the script exits with a non-zero status.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Set

from lark import Lark, Tree, exceptions


GRAMMAR_PATH = Path("docs/gramatica.ebnf")
SAMPLE_DIRS = [Path("examples"), Path("src/tests")]


def collect_rule_names(lark_parser: Lark) -> Set[str]:
    """Return the set of rule names defined in the grammar."""
    names: Set[str] = set()
    for rule in lark_parser.rules:
        name = rule.origin.name
        # ``name`` can be either ``str`` or ``Token``
        if hasattr(name, "value"):
            name = name.value
        names.add(str(name))
    return names


def visit_tree(tree: Tree, used: Set[str]) -> None:
    """Recursively visit ``tree`` collecting rule names."""
    used.add(tree.data)
    for child in tree.children:
        if isinstance(child, Tree):
            visit_tree(child, used)


def iter_sample_files(dirs: Iterable[Path]) -> Iterable[Path]:
    for base in dirs:
        if not base.exists():
            continue
        for path in base.rglob("*.co"):
            if path.is_file():
                yield path


def main(threshold: float) -> int:
    parser = Lark.open(GRAMMAR_PATH, parser="earley")
    all_rules = collect_rule_names(parser)
    used_rules: Set[str] = set()

    for file in iter_sample_files(SAMPLE_DIRS):
        try:
            tree = parser.parse(file.read_text(encoding="utf-8"))
        except exceptions.LarkError as exc:  # pragma: no cover - diagnostic
            print(f"⚠️  Error al parsear {file}: {exc}", file=sys.stderr)
            continue
        visit_tree(tree, used_rules)

    coverage = 100.0 * len(used_rules) / len(all_rules) if all_rules else 100.0

    missing = sorted(all_rules - used_rules)
    print(f"Cobertura de gramática: {coverage:.2f}% ({len(used_rules)}/{len(all_rules)})")
    if missing:
        print("Reglas no utilizadas:")
        for rule in missing:
            print(f"  - {rule}")

    if coverage < threshold:
        print(
            f"❌ Cobertura {coverage:.2f}% inferior al umbral {threshold:.2f}%",
            file=sys.stderr,
        )
        return 1

    print("✅ Cobertura suficiente")
    return 0


if __name__ == "__main__":
    argp = argparse.ArgumentParser(description="Reporte de cobertura de gramática")
    argp.add_argument(
        "--threshold",
        type=float,
        default=0.0,
        help="Porcentaje mínimo de cobertura requerido",
    )
    args = argp.parse_args()
    sys.exit(main(args.threshold))
