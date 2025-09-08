from agix.reasoning.basic import Reasoner


def test_agix_reasoner_selects_best_model():
    evaluations = [
        {"name": "A", "accuracy": 0.8, "interpretability": 0.9},
        {"name": "B", "accuracy": 0.85, "interpretability": 0.7},
        {"name": "C", "accuracy": 0.85, "interpretability": 0.8},
    ]
    result = Reasoner().select_best_model(evaluations)
    assert result["name"] == "C"
    assert "Modelo seleccionado" in result["reason"]
