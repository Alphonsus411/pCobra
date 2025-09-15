import pcobra  # garantiza rutas para submódulos
from unittest.mock import MagicMock, patch
import pytest

from ia import analizador_agix



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
        with pytest.raises(ImportError, match="Instala el paquete agix"):
            analizador_agix.generar_sugerencias("var x = 5")
