"""Regresión del contrato de sugerencias automáticas para GUI/IA.

Cada recomendación documentada debe partir de código validado por ``Lexer`` y
``Parser`` y debe proponer solo construcciones ya aceptadas por el parser.
"""

from __future__ import annotations

import pytest

from pcobra.cobra.core import Lexer, Parser, ParserError
from pcobra.core.errors import LexerError
from pcobra.gui import runtime


RECOMENDACIONES_GUI = [
    pytest.param(
        "retorno_en_funciones",
        """
func saludar(nombre):
    retorno nombre
fin
""",
        """
func saludar(nombre):
    retornar nombre
fin
""",
        "Libro §3.3 Sentencias y §3.4 Funciones: preferir retorno como forma canónica; "
        "retornar queda aceptado como forma no canónica.",
        id="retorno-en-funciones-prefiere-forma-canonica",
    ),
    pytest.param(
        "usar_importacion_con_cadena",
        """
usar "numero"
imprimir(es_finito(10))
""",
        """
usar "numero" como numero
imprimir(numero.es_finito(10))
""",
        "Libro §3.6 Módulos: `usar` no acepta alias `como`; usar importación plana.",
        id="usar-sin-alias-como",
    ),
    pytest.param(
        "funciones_con_func",
        """
func calcular_total(subtotal, impuesto):
    retorno subtotal + impuesto
fin
""",
        """
funcion calcular_total(subtotal, impuesto):
    retorno subtotal + impuesto
fin
""",
        "Libro §3.4 Funciones: el parser implementa `func`/`definir`.",
        id="func-no-funcion",
    ),
]


RECOMENDACIONES_GUI_INVALIDAS = [
    caso
    for caso in RECOMENDACIONES_GUI
    if caso.id in {"usar-sin-alias-como", "func-no-funcion"}
]

RECOMENDACIONES_GUI_ACEPTADAS_NO_RECOMENDADAS = [
    caso
    for caso in RECOMENDACIONES_GUI
    if caso.id == "retorno-en-funciones-prefiere-forma-canonica"
]


def _parsear(codigo: str):
    tokens = Lexer(codigo).tokenizar()
    return Parser(tokens).parsear()


@pytest.mark.parametrize(
    ("nombre", "fragmento_sugerido", "fragmento_invalido", "regla_libro"),
    RECOMENDACIONES_GUI,
)
def test_recomendaciones_gui_solo_proponen_fragmentos_aceptados_por_parser(
    nombre: str,
    fragmento_sugerido: str,
    fragmento_invalido: str,
    regla_libro: str,
) -> None:
    assert nombre
    assert regla_libro.startswith("Libro §3")
    ast = _parsear(fragmento_sugerido)
    assert ast


@pytest.mark.parametrize(
    ("nombre", "fragmento_sugerido", "fragmento_invalido", "regla_libro"),
    RECOMENDACIONES_GUI_INVALIDAS,
)
def test_recomendaciones_gui_cubren_ejemplos_invalidos_sin_ampliar_parser(
    nombre: str,
    fragmento_sugerido: str,
    fragmento_invalido: str,
    regla_libro: str,
) -> None:
    assert nombre
    assert fragmento_sugerido != fragmento_invalido
    assert regla_libro
    with pytest.raises(ParserError):
        _parsear(fragmento_invalido)


@pytest.mark.parametrize(
    ("nombre", "fragmento_sugerido", "fragmento_no_recomendado", "regla_libro"),
    RECOMENDACIONES_GUI_ACEPTADAS_NO_RECOMENDADAS,
)
def test_recomendaciones_gui_cubren_casos_aceptados_no_recomendados(
    nombre: str,
    fragmento_sugerido: str,
    fragmento_no_recomendado: str,
    regla_libro: str,
) -> None:
    assert nombre == "retorno_en_funciones"
    assert "preferir retorno" in regla_libro
    assert "retornar queda aceptado" in regla_libro
    assert _parsear(fragmento_sugerido)
    assert _parsear(fragmento_no_recomendado)


@pytest.mark.parametrize(
    ("codigo_invalido", "tipo_fallo"),
    [
        pytest.param(
            'imprimir("hola)',
            "Lexer",
            id="corta-si-falla-lexer",
        ),
        pytest.param(
            """
funcion calcular_total(subtotal, impuesto):
    retorno subtotal + impuesto
fin
""",
            "Parser",
            id="corta-si-falla-parser",
        ),
    ],
)
def test_reporte_sugerencias_no_invoca_motor_ia_si_lexer_o_parser_fallan(
    monkeypatch, codigo_invalido: str, tipo_fallo: str
) -> None:
    """La GUI debe cortar antes de llamar al motor IA si Lexer o Parser fallan."""

    monkeypatch.setattr(
        runtime,
        "detectar_motor_ia_sugerencias",
        lambda: runtime.MotorIASugerencias(disponible=True),
    )

    def fallar_si_se_invoca_motor(_codigo: str) -> list[str]:
        pytest.fail(f"generar_sugerencias no debe ejecutarse cuando falla {tipo_fallo}")

    monkeypatch.setattr(runtime, "generar_sugerencias", fallar_si_se_invoca_motor)

    reporte = runtime.generar_reporte_sugerencias(codigo_invalido)

    assert "Errores léxicos/sintácticos:" in reporte
    assert "Corrige primero los errores anteriores" in reporte


def test_reporte_sugerencias_codigo_valido_agrupa_por_categorias_del_libro(
    monkeypatch,
) -> None:
    """Las sugerencias válidas se muestran agrupadas por categorías del Libro."""

    monkeypatch.setattr(
        runtime,
        "detectar_motor_ia_sugerencias",
        lambda: runtime.MotorIASugerencias(disponible=True),
    )

    sugerencias_libro = [
        "Usar nombres descriptivos para variables [regla: LP-3.1-NOMBRES-DESCRIPTIVOS; §3.1 Léxico]",
        "Usar `retorno` como sentencia de salida en funciones [regla: LP-3.3-RETORNO-CANONICO; §3.3 Sentencias]",
        "Agregar una sentencia imprimir solo si aporta observabilidad [regla: LP-3.3-IMPRESION-CANONICA; §3.3 Sentencias]",
        "Declarar funciones con `func` o `definir`, no con `funcion` [regla: LP-3.9-FUNCIONES-CON-FUNC; §3.9 Contrato]",
        "Usar módulos con `usar \"modulo\"` y llamadas planas, sin alias `como` [regla: LP-3.6-USAR-SIN-ALIAS; §3.6 Módulos]",
    ]
    monkeypatch.setattr(runtime, "generar_sugerencias", lambda _codigo: sugerencias_libro)

    reporte = runtime.generar_reporte_sugerencias("total = 10\nimprimir(total)")

    assert "- No se detectaron errores con el Lexer y Parser de Cobra." in reporte
    for titulo in (
        "- Léxico/sintaxis:",
        "- Estilo:",
        "- Nombres:",
        "- Forma canónica:",
        "- Observabilidad:",
    ):
        assert titulo in reporte
    for sugerencia in sugerencias_libro:
        assert f"  - {sugerencia}" in reporte


def test_reglas_libro_programacion_declaran_fragmentos_soportados_por_parser() -> None:
    """Cada regla interna debe exponer metadatos mínimos y un fragmento parseable."""
    from pcobra.ia.reglas_libro_programacion import REGLAS_LIBRO_PROGRAMACION

    ids = {regla.id for regla in REGLAS_LIBRO_PROGRAMACION}
    assert "LP-3.3-RETORNO-CANONICO" in ids
    assert "LP-3.9-FUNCIONES-CON-FUNC" in ids

    campos_obligatorios = ("id", "seccion", "descripcion", "fragmento_valido")
    claves_metadatos = {
        "rule_id",
        "rule_section",
        "category",
        "severity",
        "automatic",
    }

    for regla in REGLAS_LIBRO_PROGRAMACION:
        for campo in campos_obligatorios:
            valor = getattr(regla, campo, None)
            assert isinstance(valor, str) and valor.strip(), (regla, campo)

        ast = _parsear(regla.fragmento_valido)
        assert ast, regla.id
        assert regla.metadatos() == {
            "rule_id": regla.id,
            "rule_section": regla.seccion,
            "category": regla.categoria,
            "severity": regla.severidad,
            "automatic": regla.aplicable_automaticamente,
        }
        assert set(regla.metadatos()) == claves_metadatos

        if regla.fragmento_no_recomendado is not None:
            assert regla.fragmento_no_recomendado.strip(), regla.id
            assert regla.fragmento_no_recomendado.strip() != regla.fragmento_valido.strip()
            try:
                ast_no_recomendado = _parsear(regla.fragmento_no_recomendado)
            except (LexerError, ParserError) as exc:
                assert str(exc), regla.id
            else:
                assert ast_no_recomendado, regla.id

        assert regla.categoria in {
            "léxico/sintaxis",
            "estilo",
            "nombres",
            "forma canónica",
            "observabilidad",
        }
        assert regla.severidad in {"informativa", "baja", "media", "alta"}
        assert isinstance(regla.aplicable_automaticamente, bool)


def test_regla_retorno_canonico_acepta_retorno_y_retornar_pero_prefiere_retorno() -> None:
    from pcobra.ia.reglas_libro_programacion import REGLAS_LIBRO_PROGRAMACION

    fragmento_retorno = """
func saludar(nombre):
    retorno nombre
fin
"""
    fragmento_retornar = """
func saludar(nombre):
    retornar nombre
fin
"""

    regla = next(
        regla
        for regla in REGLAS_LIBRO_PROGRAMACION
        if regla.id == "LP-3.3-RETORNO-CANONICO"
    )

    assert regla.fragmento_valido.strip() == fragmento_retorno.strip()
    assert regla.fragmento_no_recomendado is not None
    assert regla.fragmento_no_recomendado.strip() == fragmento_retornar.strip()
    assert "retorno" in regla.descripcion
    assert "retornar" in regla.fragmento_no_recomendado
    assert _parsear(fragmento_retorno)
    assert _parsear(fragmento_retornar)


def test_regla_funciones_con_func_cubre_caso_invalido_real() -> None:
    from pcobra.ia.reglas_libro_programacion import REGLAS_LIBRO_PROGRAMACION

    fragmento_valido = """
func calcular_total(subtotal, impuesto):
    retorno subtotal + impuesto
fin
"""
    fragmento_invalido = """
funcion calcular_total(subtotal, impuesto):
    retorno subtotal + impuesto
fin
"""

    regla = next(
        regla
        for regla in REGLAS_LIBRO_PROGRAMACION
        if regla.id == "LP-3.9-FUNCIONES-CON-FUNC"
    )
    assert regla.fragmento_valido.strip() == fragmento_valido.strip()
    assert regla.fragmento_no_recomendado is not None
    assert regla.fragmento_no_recomendado.strip() == fragmento_invalido.strip()
    assert _parsear(fragmento_valido)
    with pytest.raises(ParserError):
        _parsear(regla.fragmento_no_recomendado)
