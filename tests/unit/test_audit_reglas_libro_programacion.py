"""Contrato CI para que las reglas IA no queden huérfanas respecto al Libro."""

from __future__ import annotations

from scripts.ci.audit_reglas_libro_programacion import auditar


def test_reglas_libro_programacion_no_quedan_huerfanas() -> None:
    """Falla si una regla referencia una sección ausente o un fragmento no parseable."""
    assert auditar() == []
