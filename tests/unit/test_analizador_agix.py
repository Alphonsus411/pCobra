import pcobra  # garantiza rutas para submódulos
from unittest.mock import MagicMock, patch
import pytest

from pcobra.ia import analizador_agix


def test_generar_sugerencias_variable_descriptiva():
    """Verifica que se retorne la sugerencia adecuada."""
    instancia_falsa = MagicMock()
    instancia_falsa.select_best_model.return_value = {
        "reason": "Usar nombres descriptivos para variables"
    }
    with patch.object(analizador_agix, "Reasoner", return_value=instancia_falsa):
        sugerencias = analizador_agix.generar_sugerencias("var x = 5")
    assert sugerencias == ["Usar nombres descriptivos para variables"]


def test_generar_sugerencias_modulacion_emocional():
    instancia = MagicMock()
    instancia.select_best_model.return_value = {"reason": "Usar nombres descriptivos"}
    with patch.object(analizador_agix, "Reasoner", return_value=instancia):
        with patch.object(analizador_agix, "PADState") as pad_mock:
            analizador_agix.generar_sugerencias(
                "var x = 5", placer=0.1, activacion=0.2, dominancia=-0.3
            )
    pad_mock.assert_called_once_with(0.1, 0.2, -0.3)
    instancia.modular_por_emocion.assert_called_once_with(pad_mock.return_value)


def test_generar_sugerencias_sin_agix():
    with patch.object(analizador_agix, "Reasoner", None):
        with pytest.raises(
            ImportError, match="dependencia opcional 'agix'.*pip install agix"
        ):
            analizador_agix.generar_sugerencias("var x = 5")


def test_import_opcional_sin_agix_muestra_mensaje_claro(monkeypatch):
    """Verifica que importar el analizador sin agix no rompa y falle con ayuda clara."""
    import builtins
    import importlib

    import_original = builtins.__import__

    def bloquear_agix(nombre, *args, **kwargs):
        if nombre == "agix" or nombre.startswith("agix."):
            raise ImportError("agix bloqueado para la prueba")
        return import_original(nombre, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", bloquear_agix)
    recargado = importlib.reload(analizador_agix)

    try:
        assert recargado.Reasoner is None
        with pytest.raises(
            ImportError, match="dependencia opcional 'agix'.*pip install agix"
        ):
            recargado.generar_sugerencias("var x = 5")
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
    with patch.object(analizador_agix, "Reasoner", MagicMock()):
        with pytest.raises(ValueError, match=rf"{param} debe estar en el rango"):
            analizador_agix.generar_sugerencias("var x = 5", **{param: valor})


def test_error_lexico_o_sintactico_impide_sugerencias_aplicables():
    """No se invoca agix si Lexer/Parser rechazan el fragmento."""
    razonador = MagicMock()
    with patch.object(
        analizador_agix, "Reasoner", return_value=razonador
    ) as razonador_cls:
        with pytest.raises(Exception):
            analizador_agix.generar_sugerencias(
                "funcion saludar(nombre): retornar nombre"
            )
    razonador_cls.assert_not_called()
    razonador.select_best_model.assert_not_called()


def test_sugerencias_no_inventan_construcciones_fuera_del_parser():
    """Los candidatos salen de reglas validadas y evitan formas no aceptadas."""
    instancia = MagicMock()

    def seleccionar_primero(evaluaciones):
        return evaluaciones[0]

    instancia.select_best_model.side_effect = seleccionar_primero
    with patch.object(analizador_agix, "Reasoner", return_value=instancia):
        sugerencias = analizador_agix.generar_sugerencias("var x = 5")

    texto = "\n".join(sugerencias)
    assert "retornar" not in texto
    assert "funcion " not in texto
    evaluaciones = instancia.select_best_model.call_args.args[0]
    assert all("rule_id" in evaluacion for evaluacion in evaluaciones)
    assert all("rule_section" in evaluacion for evaluacion in evaluaciones)


def test_sugerencia_principal_referencia_regla_interna_trazable():
    instancia = MagicMock()

    def seleccionar_primero(evaluaciones):
        return evaluaciones[0]

    instancia.select_best_model.side_effect = seleccionar_primero
    with patch.object(analizador_agix, "Reasoner", return_value=instancia):
        sugerencias = analizador_agix.generar_sugerencias("var x = 5")

    assert len(sugerencias) == 1
    assert "[regla: LP-" in sugerencias[0]
    assert "§3." in sugerencias[0]
