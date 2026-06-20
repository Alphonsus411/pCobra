"""Pruebas del reporte GUI de corrección tipográfica no destructiva."""

from __future__ import annotations

import pytest

from pcobra.gui import runtime


@pytest.fixture(autouse=True)
def _motor_disponible(monkeypatch):
    monkeypatch.setattr(
        runtime,
        "detectar_motor_ia_sugerencias",
        lambda: runtime.MotorIASugerencias(disponible=True),
    )


def test_correccion_codigo_valido_muestra_sugerencias_detalladas(monkeypatch):
    monkeypatch.setattr(
        runtime,
        "generar_sugerencias",
        lambda _codigo: [
            "Usar nombres descriptivos para variables [regla: LP-3.1-NOMBRES-DESCRIPTIVOS; §3.1 Léxico]",
        ],
    )

    reporte = runtime.generar_reporte_correccion_tipografica("x = 1\nimprimir(x)")

    assert "- No se detectaron errores con el Lexer y Parser de Cobra." in reporte
    assert "Corrección tipográfica del Libro:" in reporte
    assert "Regla: LP-3.1-NOMBRES-DESCRIPTIVOS" in reporte
    assert "Sección: §3.1 Léxico" in reporte
    assert "Ubicación: línea 1" in reporte
    assert "Explicación: Usar nombres descriptivos para variables" in reporte
    assert "Nota: el editor no se modifica automáticamente." in reporte


def test_correccion_codigo_invalido_bloquea_motor_por_parser(monkeypatch):
    def fallar_si_invoca_motor(_codigo: str) -> list[str]:
        pytest.fail("No debe invocar el motor IA con código inválido")

    monkeypatch.setattr(runtime, "generar_sugerencias", fallar_si_invoca_motor)

    reporte = runtime.generar_reporte_correccion_tipografica(
        """
funcion calcular_total(subtotal, impuesto):
    retorno subtotal + impuesto
fin
"""
    )

    assert "Errores léxicos/sintácticos:" in reporte
    assert "Corrige primero los errores anteriores" in reporte
    assert "Corrección tipográfica del Libro:" in reporte


def test_correccion_motor_ia_no_disponible(monkeypatch):
    monkeypatch.setattr(
        runtime,
        "detectar_motor_ia_sugerencias",
        lambda: runtime.MotorIASugerencias(
            disponible=False,
            detalle="Motor IA de pruebas no disponible.",
        ),
    )
    monkeypatch.setattr(
        runtime,
        "generar_sugerencias",
        lambda _codigo: pytest.fail("No debe invocar motor no disponible"),
    )

    reporte = runtime.generar_reporte_correccion_tipografica("total = 10")

    assert "- No se detectaron errores con el Lexer y Parser de Cobra." in reporte
    assert "Motor IA de pruebas no disponible." in reporte


def test_correccion_formato_de_salida_agrupado(monkeypatch):
    monkeypatch.setattr(
        runtime,
        "generar_sugerencias",
        lambda _codigo: [
            "Usar `retorno` como sentencia de salida en funciones [regla: LP-3.3-RETORNO-CANONICO; §3.3 Sentencias]",
            "Usar módulos con `usar \"modulo\"` y llamadas planas [regla: LP-3.6-USAR-SIN-ALIAS; §3.6 Módulos]",
        ],
    )

    reporte = runtime.generar_reporte_correccion_tipografica(
        'usar "numero"\nfunc saludar(nombre):\n    retorno nombre\nfin\n'
    )

    assert "- Estilo:" in reporte
    assert "- Forma canónica:" in reporte
    assert "Regla: LP-3.6-USAR-SIN-ALIAS" in reporte
    assert "Ubicación: línea 1" in reporte
    assert "Regla: LP-3.3-RETORNO-CANONICO" in reporte
    assert "Ubicación: línea 3" in reporte
