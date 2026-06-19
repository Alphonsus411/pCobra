#!/usr/bin/env python3
"""Audita la trazabilidad de reglas IA contra el Libro de Programación Cobra.

El script lee ``src/pcobra/ia/reglas_libro_programacion.py`` con ``ast`` para
extraer los metadatos declarados en ``REGLAS_LIBRO_PROGRAMACION`` sin ejecutar
el módulo, comprueba que cada sección exista en el Libro y valida cada
``fragmento_valido`` con el ``Lexer`` y ``Parser`` oficiales.
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGLAS_PATH = ROOT / "src" / "pcobra" / "ia" / "reglas_libro_programacion.py"
LIBRO_PATH = ROOT / "docs" / "LIBRO_PROGRAMACION_COBRA.md"
SRC_PATH = ROOT / "src"


@dataclass(frozen=True)
class ReglaAuditada:
    """Campos estáticos requeridos para auditar una regla del Libro."""

    id: str
    seccion: str
    fragmento_valido: str


def _literal_str(node: ast.AST, *, campo: str, regla: str) -> str:
    """Devuelve un literal de cadena o falla con un mensaje accionable."""
    try:
        valor = ast.literal_eval(node)
    except (SyntaxError, ValueError) as exc:
        raise ValueError(f"{regla}: el campo {campo!r} debe ser literal") from exc
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{regla}: el campo {campo!r} debe ser una cadena no vacía")
    return valor


def _extraer_reglas(reglas_path: Path = REGLAS_PATH) -> list[ReglaAuditada]:
    """Extrae ``id``, ``seccion`` y ``fragmento_valido`` desde el AST del módulo."""
    tree = ast.parse(reglas_path.read_text(encoding="utf-8"), filename=str(reglas_path))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "REGLAS_LIBRO_PROGRAMACION"
            for target in node.targets
        ):
            return _extraer_reglas_desde_tuple(node.value)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "REGLAS_LIBRO_PROGRAMACION" and node.value is not None:
                return _extraer_reglas_desde_tuple(node.value)
    raise ValueError(f"No se encontró REGLAS_LIBRO_PROGRAMACION en {reglas_path}")


def _extraer_reglas_desde_tuple(node: ast.AST) -> list[ReglaAuditada]:
    if not isinstance(node, ast.Tuple):
        raise ValueError("REGLAS_LIBRO_PROGRAMACION debe declararse como una tupla literal")

    reglas: list[ReglaAuditada] = []
    for index, element in enumerate(node.elts, start=1):
        if not isinstance(element, ast.Call):
            raise ValueError(f"Regla #{index}: se esperaba una llamada a ReglaLibroProgramacion")
        kwargs = {keyword.arg: keyword.value for keyword in element.keywords if keyword.arg}
        regla_id = _literal_str(
            kwargs.get("id", ast.Constant(value="")), campo="id", regla=f"Regla #{index}"
        )
        seccion = _literal_str(
            kwargs.get("seccion", ast.Constant(value="")), campo="seccion", regla=regla_id
        )
        fragmento_valido = _literal_str(
            kwargs.get("fragmento_valido", ast.Constant(value="")),
            campo="fragmento_valido",
            regla=regla_id,
        )
        reglas.append(ReglaAuditada(regla_id, seccion, fragmento_valido))
    if not reglas:
        raise ValueError("REGLAS_LIBRO_PROGRAMACION no puede estar vacía")
    return reglas


def _normalizar_seccion(seccion: str) -> tuple[str, str]:
    match = re.fullmatch(r"§(?P<num>\d+(?:\.\d+)*)\s+(?P<title>.+)", seccion.strip())
    if not match:
        raise ValueError(
            f"Sección inválida {seccion!r}: usa el formato '§N[.N] Título'"
        )
    return match.group("num"), " ".join(match.group("title").split()).casefold()


def _extraer_secciones_libro(libro_path: Path = LIBRO_PATH) -> set[tuple[str, str]]:
    contenido = libro_path.read_text(encoding="utf-8")
    secciones: set[tuple[str, str]] = set()
    for line in contenido.splitlines():
        match = re.match(r"^#{2,6}\s+(?P<num>\d+(?:\.\d+)*)(?:\)|\.)?\s+(?P<title>.+?)\s*$", line)
        if match:
            secciones.add(
                (match.group("num"), " ".join(match.group("title").split()).casefold())
            )
    return secciones


def _validar_fragmento_parseable(regla: ReglaAuditada) -> None:
    if str(SRC_PATH) not in sys.path:
        sys.path.insert(0, str(SRC_PATH))
    from pcobra.cobra.core import Lexer, Parser

    tokens = Lexer(regla.fragmento_valido).tokenizar()
    Parser(tokens).parsear()


def auditar() -> list[str]:
    """Ejecuta la auditoría y devuelve una lista de errores encontrados."""
    errores: list[str] = []
    try:
        reglas = _extraer_reglas()
    except Exception as exc:  # pragma: no cover - ruta defensiva para CI
        return [f"No se pudieron extraer las reglas: {exc}"]

    secciones_libro = _extraer_secciones_libro()
    ids_vistos: set[str] = set()
    for regla in reglas:
        if regla.id in ids_vistos:
            errores.append(f"{regla.id}: id duplicado")
        ids_vistos.add(regla.id)

        try:
            seccion = _normalizar_seccion(regla.seccion)
        except ValueError as exc:
            errores.append(f"{regla.id}: {exc}")
        else:
            if seccion not in secciones_libro:
                errores.append(
                    f"{regla.id}: sección huérfana {regla.seccion!r}; no existe en {LIBRO_PATH}"
                )

        try:
            _validar_fragmento_parseable(regla)
        except Exception as exc:
            errores.append(
                f"{regla.id}: fragmento_valido no parsea con Lexer/Parser: {exc}"
            )
    return errores


def main() -> int:
    errores = auditar()
    if errores:
        print("Auditoría de reglas del Libro: ERROR", file=sys.stderr)
        for error in errores:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Auditoría de reglas del Libro: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
