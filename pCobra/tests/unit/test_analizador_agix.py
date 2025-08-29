import backend  # garantiza rutas para submódulos
from unittest.mock import MagicMock, patch

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
