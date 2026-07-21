import pcobra  # garantiza rutas para submódulos
from pathlib import Path
from unittest.mock import create_autospec, patch
import tomllib

import pytest

from pcobra.ia import analizador_agix, analizador_sugerencias
from pcobra.ia.reglas_libro_programacion import construir_candidatos_desde_reglas


def _doble_reasoner():
    """Crea clase e instancia que respetan el contrato público de AGIX 1.11."""
    clase = create_autospec(analizador_agix.Reasoner, spec_set=True)
    return clase, clase.return_value


def _doble_pad_state():
    """Crea un constructor limitado a la firma pública de ``PADState``."""
    return create_autospec(analizador_agix.PADState, spec_set=True)


def test_generar_sugerencias_variable_descriptiva():
    """Normaliza la respuesta real documentada por AGIX 1.11 a ``list[str]``."""
    reasoner_cls, instancia_falsa = _doble_reasoner()
    instancia_falsa.select_best_model.return_value = {
        "name": "nombres descriptivos",
        "accuracy": 0.9,
        "reason": "Usar nombres descriptivos para variables",
    }
    with patch.object(analizador_agix, "Reasoner", reasoner_cls):
        sugerencias = analizador_agix.generar_sugerencias("var x = 5")
    reasoner_cls.assert_called_once_with()
    instancia_falsa.select_best_model.assert_called_once()
    assert isinstance(sugerencias, list)
    assert sugerencias == ["Usar nombres descriptivos para variables"]


def test_generar_sugerencias_rechaza_respuesta_agix_incompleta():
    """Una respuesta sin campos obligatorios se traduce sin filtrar el objeto."""
    reasoner_cls, instancia = _doble_reasoner()
    instancia.select_best_model.return_value = {
        "name": "nombres descriptivos",
        "accuracy": 0.9,
    }

    with patch.object(analizador_agix, "Reasoner", reasoner_cls):
        with pytest.raises(
            analizador_agix.RespuestaAGIXInvalidaError,
            match="AGIX devolvió una respuesta inválida.*campos obligatorios",
        ) as capturado:
            analizador_agix.generar_sugerencias("var x = 5")

    assert isinstance(capturado.value.__cause__, KeyError)


def test_generar_sugerencias_modulacion_emocional():
    reasoner_cls, instancia = _doble_reasoner()
    pad_mock = _doble_pad_state()
    instancia.select_best_model.return_value = {
        "name": "nombres descriptivos",
        "accuracy": 0.9,
        "reason": "Usar nombres descriptivos",
    }
    with patch.object(analizador_agix, "Reasoner", reasoner_cls):
        with patch.object(analizador_agix, "PADState", pad_mock):
            analizador_agix.generar_sugerencias(
                "var x = 5", placer=0.1, activacion=0.2, dominancia=-0.3
            )
    pad_mock.assert_called_once_with(0.1, 0.2, -0.3)
    instancia.modular_por_emocion.assert_called_once_with(pad_mock.return_value)


def test_generar_sugerencias_sin_agix():
    with patch.object(analizador_agix, "Reasoner", None):
        with pytest.raises(
            ImportError, match="dependencia oficial 'agix'.*pip install agix"
        ):
            analizador_agix.generar_sugerencias("var x = 5")


def test_import_opcional_sin_agix_muestra_mensaje_claro(monkeypatch):
    """Verifica que importar el analizador sin agix no rompa y falle con ayuda clara."""
    import builtins
    import importlib

    import_original = builtins.__import__

    def bloquear_agix(nombre, *args, **kwargs):
        if nombre == "agix" or nombre.startswith("agix."):
            raise ModuleNotFoundError("No module named 'agix'", name="agix")
        return import_original(nombre, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", bloquear_agix)
    recargado = importlib.reload(analizador_agix)

    try:
        assert recargado.Reasoner is None
        with pytest.raises(
            ImportError, match="dependencia oficial 'agix'.*pip install agix"
        ):
            recargado.generar_sugerencias("var x = 5")
    finally:
        monkeypatch.setattr(builtins, "__import__", import_original)
        importlib.reload(analizador_agix)


def test_import_agix_no_oculta_fallos_inesperados(monkeypatch):
    """Un error interno de la distribución conserva su causa original."""
    import builtins
    import importlib

    import_original = builtins.__import__
    fallo_interno = ModuleNotFoundError(
        "No module named 'dependencia_interna'", name="dependencia_interna"
    )

    def romper_dependencia_interna(nombre, *args, **kwargs):
        if nombre == "agix.emotion.emotion_simulator":
            raise fallo_interno
        return import_original(nombre, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", romper_dependencia_interna)
    try:
        with pytest.raises(ModuleNotFoundError) as capturado:
            importlib.reload(analizador_agix)
        assert capturado.value is fallo_interno
    finally:
        monkeypatch.setattr(builtins, "__import__", import_original)
        importlib.reload(analizador_agix)


@pytest.mark.parametrize(
    "param, valor",
    [
        ("placer", 2.0),
        ("activacion", -1.5),
        ("dominancia", 1.2),
    ],
)
def test_generar_sugerencias_valores_fuera_de_rango(param, valor):
    reasoner_cls, _ = _doble_reasoner()
    with patch.object(analizador_agix, "Reasoner", reasoner_cls):
        with pytest.raises(ValueError, match=rf"{param} debe estar en el rango"):
            analizador_agix.generar_sugerencias("var x = 5", **{param: valor})


def test_error_lexico_o_sintactico_impide_sugerencias_aplicables():
    """No se invoca agix si Lexer/Parser rechazan el fragmento."""
    razonador_cls, razonador = _doble_reasoner()
    with patch.object(analizador_agix, "Reasoner", razonador_cls):
        with pytest.raises(Exception):
            analizador_agix.generar_sugerencias(
                "funcion saludar(nombre): retornar nombre"
            )
    razonador_cls.assert_not_called()
    razonador.select_best_model.assert_not_called()


@pytest.mark.parametrize(
    "codigo_invalido",
    [
        "var x = 5 ¿",
        "var x =",
    ],
)
def test_generar_sugerencias_rechaza_codigo_invalido_antes_de_agix(codigo_invalido):
    """Lexer/Parser deben bloquear Agix tanto para errores léxicos como sintácticos."""

    razonador_cls, razonador = _doble_reasoner()
    with patch.object(analizador_agix, "Reasoner", razonador_cls):
        with pytest.raises(Exception):
            analizador_agix.generar_sugerencias(codigo_invalido)

    razonador_cls.assert_not_called()
    razonador.select_best_model.assert_not_called()


def test_generar_sugerencias_codigo_valido_expone_regla_nombres_descriptivos():
    """Un programa Cobra válido puede activar LP-3.1 tras pasar Lexer/Parser."""

    reasoner_cls, instancia = _doble_reasoner()
    instancia.select_best_model.side_effect = lambda evaluaciones: next(
        ev
        for ev in evaluaciones
        if ev["rule_id"] == "LP-3.1-NOMBRES-DESCRIPTIVOS"
    )

    with patch.object(analizador_agix, "Reasoner", reasoner_cls):
        sugerencias = analizador_agix.generar_sugerencias("var x = 5")

    assert sugerencias == [
        "Usar nombres descriptivos para variables "
        "[regla: LP-3.1-NOMBRES-DESCRIPTIVOS; §3.1 Léxico]"
    ]
    evaluaciones = instancia.select_best_model.call_args.args[0]
    assert any(
        ev["rule_id"] == "LP-3.1-NOMBRES-DESCRIPTIVOS" for ev in evaluaciones
    )


def test_reglas_libro_programacion_validan_entrada_antes_de_candidatos():
    """Las reglas internas no producen candidatos si falla el Parser."""

    with pytest.raises(Exception):
        construir_candidatos_desde_reglas("var x =")


def test_sugerencias_no_inventan_construcciones_fuera_del_parser():
    """Los candidatos salen de reglas validadas y evitan formas no aceptadas."""
    reasoner_cls, instancia = _doble_reasoner()

    def seleccionar_primero(evaluaciones):
        return evaluaciones[0]

    instancia.select_best_model.side_effect = seleccionar_primero
    with patch.object(analizador_agix, "Reasoner", reasoner_cls):
        sugerencias = analizador_agix.generar_sugerencias("var x = 5")

    texto = "\n".join(sugerencias)
    assert "retornar" not in texto
    assert "funcion " not in texto
    evaluaciones = instancia.select_best_model.call_args.args[0]
    assert all("rule_id" in evaluacion for evaluacion in evaluaciones)
    assert all("rule_section" in evaluacion for evaluacion in evaluaciones)


def test_sugerencia_principal_referencia_regla_interna_trazable():
    reasoner_cls, instancia = _doble_reasoner()

    def seleccionar_primero(evaluaciones):
        return evaluaciones[0]

    instancia.select_best_model.side_effect = seleccionar_primero
    with patch.object(analizador_agix, "Reasoner", reasoner_cls):
        sugerencias = analizador_agix.generar_sugerencias("var x = 5")

    assert len(sugerencias) == 1
    assert "[regla: LP-" in sugerencias[0]
    assert "§3." in sugerencias[0]


def test_generar_sugerencias_pasa_argumentos_y_propaga_excepcion_oficial_agix():
    """Los pesos llegan a AGIX y ``ValueError`` del motor no se transforma."""
    reasoner_cls, instancia = _doble_reasoner()
    error_agix = ValueError("evaluaciones rechazadas por AGIX")
    instancia.select_best_model.side_effect = error_agix

    with patch.object(analizador_agix, "Reasoner", reasoner_cls):
        with pytest.raises(ValueError) as capturado:
            analizador_agix.generar_sugerencias(
                "var x = 5", peso_precision=0.5, peso_interpretabilidad=2.0
            )

    assert capturado.value is error_agix
    evaluaciones = instancia.select_best_model.call_args.args[0]
    assert all(0.0 <= evaluacion["accuracy"] <= 0.5 for evaluacion in evaluaciones)
    assert all(
        evaluacion["interpretability"] >= 0.0 for evaluacion in evaluaciones
    )


def test_motor_canonico_es_agix_y_no_agi_core():
    """El contrato público mantiene agix como dependencia oficial y fachada GUI."""

    pyproject = tomllib.loads(Path("pyproject.toml").read_text())
    dependencias = pyproject["project"]["dependencies"]
    requirements_docs = Path("docs/requirements.txt").read_text()
    libro = Path("docs/LIBRO_PROGRAMACION_COBRA.md").read_text(encoding="utf-8")

    assert any(dep.startswith("agix") for dep in dependencias)
    assert not any(dep.startswith("agi-core") for dep in dependencias)
    assert "agix==" in requirements_docs
    assert "agi-core" not in requirements_docs
    assert analizador_sugerencias.MOTOR_SUGERENCIAS == "agix"
    assert "Motor real de sugerencias: Cobra mantiene `agix`" in libro
    assert "agi-core" not in libro
