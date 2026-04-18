#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
LIBRO_PATH = ROOT / "docs" / "LIBRO_PROGRAMACION_COBRA.md"
GRAMMAR_PATH = ROOT / "docs" / "gramatica.ebnf"
SPEC_PATH = ROOT / "docs" / "SPEC_COBRA.md"
CLI_DIRS = [
    ROOT / "src" / "pcobra" / "cobra" / "cli" / "commands",
    ROOT / "src" / "pcobra" / "cobra" / "cli" / "commands_v2",
]
STDLIB_SRC_DIR = ROOT / "src" / "pcobra" / "standard_library"
STDLIB_DOCS_DIR = ROOT / "docs" / "standard_library"

SECTION_MARKERS = {
    "syntax": ("<!-- BEGIN: AUTO-SYNTAX-INDEX -->", "<!-- END: AUTO-SYNTAX-INDEX -->"),
    "cli": ("<!-- BEGIN: AUTO-CLI-TABLE -->", "<!-- END: AUTO-CLI-TABLE -->"),
    "stdlib": ("<!-- BEGIN: AUTO-STDLIB-INDEX -->", "<!-- END: AUTO-STDLIB-INDEX -->"),
}
STDLIB_DOC_MARKERS = ("<!-- BEGIN: AUTO-STDLIB-FUNCTIONS -->", "<!-- END: AUTO-STDLIB-FUNCTIONS -->")


@dataclass(frozen=True)
class CliCommand:
    name: str
    capability: str
    class_name: str
    path: Path


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _parse_quoted_literals(text: str) -> list[str]:
    return sorted({m.group(1) for m in re.finditer(r'"([^"\n]+)"', text) if m.group(1).strip()})


def _parse_grammar_structure(grammar: str) -> dict[str, list[str]]:
    rules: dict[str, str] = {}
    current: str | None = None
    rhs_lines: list[str] = []
    for raw_line in grammar.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        match = re.match(r"^\??([a-z_]+):\s*(.*)$", line)
        if match:
            if current is not None:
                rules[current] = " ".join(rhs_lines).strip()
            current = match.group(1)
            rhs_lines = [match.group(2).strip()]
            continue
        if current is not None and line.lstrip().startswith("|"):
            rhs_lines.append(line.strip())
            continue
        if current is not None:
            rules[current] = " ".join(rhs_lines).strip()
            current = None
            rhs_lines = []
    if current is not None:
        rules[current] = " ".join(rhs_lines).strip()

    statement_rhs = rules.get("statement", "")
    statements = [part.strip() for part in re.split(r"\s*\|\s*", statement_rhs) if part.strip()]

    expr_rhs = rules.get("expr", "")
    expr_parts = [part.strip() for part in re.split(r"\s*\|\s*", expr_rhs) if part.strip()]

    valor_rhs = rules.get("valor", "")
    valor_parts = [part.strip() for part in re.split(r"\s*\|\s*", valor_rhs) if part.strip()]

    structures = [
        "funcion",
        "funcion_asincronica",
        "clase",
        "condicional",
        "bucle_mientras",
        "bucle_para",
        "switch",
        "try_catch",
        "with_stmt",
        "macro",
        "garantia",
    ]
    structures = [s for s in structures if s in rules]

    return {
        "statements": sorted(set(statements)),
        "expressions": sorted(set(expr_parts)),
        "values": sorted(set(valor_parts)),
        "structures": structures,
    }


def _extract_tokens_from_spec(spec_text: str) -> list[str]:
    header = "## Tokens y palabras reservadas"
    start = spec_text.find(header)
    if start < 0:
        return []
    end = spec_text.find("## ", start + len(header))
    section = spec_text[start : (len(spec_text) if end < 0 else end)]
    tokens = sorted(set(re.findall(r"`([^`]+)`", section)))
    clean: list[str] = []
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        if "/" in token or "..." in token or "[^" in token:
            continue
        clean.append(token)
    return clean


def build_syntax_index() -> str:
    grammar_text = _read(GRAMMAR_PATH)
    spec_text = _read(SPEC_PATH)

    grammar_literals = [tok for tok in _parse_quoted_literals(grammar_text) if re.fullmatch(r"[A-Za-z_][\\w ]*|[^\\w\\s]", tok)]
    grammar_structure = _parse_grammar_structure(grammar_text)
    spec_tokens = _extract_tokens_from_spec(spec_text)
    lexical_tokens = sorted(set(re.findall(r"^([A-Z][A-Z_]+):", grammar_text, flags=re.MULTILINE)))

    parts: list[str] = []
    parts.append("### Índice de sintaxis (autogenerado)\n")
    parts.append("#### Tokens léxicos\n")
    for tok in lexical_tokens:
        parts.append(f"- `{tok}`")

    parts.append("\n#### Palabras reservadas (gramática + SPEC)\n")
    for tok in sorted(set(grammar_literals + spec_tokens)):
        parts.append(f"- `{tok}`")

    parts.append("\n#### Estructuras\n")
    for structure in grammar_structure["structures"]:
        parts.append(f"- `{structure}`")

    parts.append("\n#### Expresiones\n")
    for expr in grammar_structure["expressions"]:
        parts.append(f"- `{expr}`")
    parts.append("\n**Valores permitidos en expresiones**")
    for value in grammar_structure["values"]:
        parts.append(f"- `{value}`")

    parts.append("\n#### Sentencias\n")
    for stmt in grammar_structure["statements"]:
        parts.append(f"- `{stmt}`")

    return "\n".join(parts).strip() + "\n"


def _literal_str(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _collect_class_string_attr(class_node: ast.ClassDef, attr: str) -> str:
    for node in class_node.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == attr:
                    value = _literal_str(node.value)
                    if value:
                        return value
    return "-"


def _extract_cli_commands() -> list[CliCommand]:
    commands: list[CliCommand] = []
    for directory in CLI_DIRS:
        for path in sorted(directory.glob("*_cmd.py")):
            tree = ast.parse(_read(path), filename=str(path))
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    base_names = {b.id for b in node.bases if isinstance(b, ast.Name)}
                    if "BaseCommand" not in base_names:
                        continue
                    name = _collect_class_string_attr(node, "name")
                    if name == "-":
                        continue
                    capability = _collect_class_string_attr(node, "capability")
                    commands.append(
                        CliCommand(
                            name=name,
                            capability=capability,
                            class_name=node.name,
                            path=path.relative_to(ROOT),
                        )
                    )
    commands.sort(key=lambda c: (c.name, str(c.path)))
    return commands


def build_cli_table() -> str:
    commands = _extract_cli_commands()
    lines = ["### Tabla CLI actualizada (autogenerado)", "", "| Comando | Capacidad | Clase | Archivo |", "|---|---|---|---|"]
    for cmd in commands:
        lines.append(
            f"| `{cmd.name}` | `{cmd.capability}` | `{cmd.class_name}` | `{cmd.path.as_posix()}` |"
        )
    return "\n".join(lines).strip() + "\n"


def _extract_public_functions_from_module(path: Path) -> list[str]:
    tree = ast.parse(_read(path), filename=str(path))
    exported: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__" and isinstance(node.value, (ast.List, ast.Tuple)):
                    for elt in node.value.elts:
                        text = _literal_str(elt)
                        if text:
                            exported.append(text)
    if exported:
        return sorted(dict.fromkeys(exported))

    funcs = [node.name for node in tree.body if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")]
    return sorted(dict.fromkeys(funcs))


def _replace_or_append_block(text: str, begin: str, end: str, body: str, heading_hint: str | None = None) -> str:
    block = f"{begin}\n{body.rstrip()}\n{end}"
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), flags=re.DOTALL)
    if pattern.search(text):
        return pattern.sub(block, text)

    if heading_hint and heading_hint in text:
        insert_at = text.index(heading_hint) + len(heading_hint)
        return text[:insert_at] + "\n\n" + block + text[insert_at:]

    return text.rstrip() + "\n\n" + block + "\n"


def sync_stdlib_docs() -> list[Path]:
    touched: list[Path] = []
    modules = sorted(p for p in STDLIB_SRC_DIR.glob("*.py") if p.stem != "__init__")
    for module_path in modules:
        module = module_path.stem
        funcs = _extract_public_functions_from_module(module_path)
        doc_path = STDLIB_DOCS_DIR / f"{module}.md"
        if doc_path.exists():
            content = _read(doc_path)
        else:
            content = f"# `standard_library.{module}`\n\nDocumentación sincronizada automáticamente desde `src/pcobra/standard_library/{module}.py`.\n"

        body = "\n".join(
            [
                f"## API pública sincronizada (`standard_library.{module}`)",
                "",
                "| Función |",
                "|---|",
                *[f"| `{f}` |" for f in funcs],
            ]
        )
        updated = _replace_or_append_block(content, STDLIB_DOC_MARKERS[0], STDLIB_DOC_MARKERS[1], body)
        if updated != content:
            _write(doc_path, updated)
            touched.append(doc_path)
    return touched


def build_stdlib_index() -> str:
    modules = sorted(p for p in STDLIB_SRC_DIR.glob("*.py") if p.stem != "__init__")
    lines = ["### Índice de módulos y funciones de `standard_library` (autogenerado)", ""]
    for module_path in modules:
        module = module_path.stem
        funcs = _extract_public_functions_from_module(module_path)
        doc_rel = f"docs/standard_library/{module}.md"
        lines.append(f"- **`{module}`** ({len(funcs)} funciones) → `{doc_rel}`")
        preview = ", ".join(f"`{name}`" for name in funcs[:8])
        if len(funcs) > 8:
            preview += ", ..."
        lines.append(f"  - API: {preview}")
    return "\n".join(lines).strip() + "\n"


def sync_libro() -> bool:
    libro = _read(LIBRO_PATH)
    updated = libro

    updated = _replace_or_append_block(
        updated,
        *SECTION_MARKERS["syntax"],
        build_syntax_index(),
        heading_hint="## 3) Sintaxis base del lenguaje",
    )
    updated = _replace_or_append_block(
        updated,
        *SECTION_MARKERS["cli"],
        build_cli_table(),
        heading_hint="## 10) CLI de Cobra para desarrollo diario",
    )
    updated = _replace_or_append_block(
        updated,
        *SECTION_MARKERS["stdlib"],
        build_stdlib_index(),
        heading_hint="## 12) Biblioteca estándar (corelibs / standard library)",
    )

    if updated != libro:
        _write(LIBRO_PATH, updated)
        return True
    return False


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sincroniza secciones autogeneradas del libro Cobra.")
    parser.add_argument("--check", action="store_true", help="Solo verifica drift sin escribir cambios.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    before_libro = _read(LIBRO_PATH)
    pre_docs = {p: _read(p) for p in STDLIB_DOCS_DIR.glob("*.md")}

    changed_libro = sync_libro()
    touched_stdlib_docs = sync_stdlib_docs()

    if args.check:
        drift = False
        after_libro = _read(LIBRO_PATH)
        if after_libro != before_libro:
            drift = True
            _write(LIBRO_PATH, before_libro)

        for path, before in pre_docs.items():
            if path.exists() and _read(path) != before:
                drift = True
                _write(path, before)

        # borrar docs creados en check
        for created in [p for p in touched_stdlib_docs if p not in pre_docs]:
            if created.exists():
                created.unlink()
                drift = True

        if drift:
            print("Drift detectado: ejecuta `python scripts/sync_libro_programacion.py`.")
            return 1
        print("Sin drift documental.")
        return 0

    if changed_libro or touched_stdlib_docs:
        print("Secciones documentales sincronizadas.")
    else:
        print("No hubo cambios.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
