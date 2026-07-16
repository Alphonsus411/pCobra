from pathlib import Path


DOC = Path("docs/seguimiento_auditoria_tecnica.md")
ESTADOS = {"pendiente", "en investigación", "parcial", "corregido", "verificado", "regresión"}


def test_seguimiento_auditoria_tecnica_cubre_problemas_y_estados_permitidos():
    contenido = DOC.read_text(encoding="utf-8")

    for problema in range(1, 16):
        assert f"| Fase " in contenido and f"| {problema} |" in contenido

    for linea in contenido.splitlines():
        if not linea.startswith("| Fase "):
            continue
        columnas = [columna.strip() for columna in linea.strip("|").split("|")]
        if len(columnas) >= 4 and columnas[1].isdigit():
            assert columnas[2] in ESTADOS


def test_seguimiento_documenta_pendientes_conocidos_sin_marcar_como_verificados():
    contenido = DOC.read_text(encoding="utf-8")

    assert "`validar-sintaxis` como comando público | pendiente" in contenido
    assert "Suite completa `pytest -q` | en investigación" in contenido
    assert "Lexer, Parser y gramática no se modificaron" in contenido
