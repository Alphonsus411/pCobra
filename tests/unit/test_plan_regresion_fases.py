from pathlib import Path


PLAN = Path("docs/plan_regresion_fases.md")


def test_plan_regresion_fases_usa_comandos_python_reales():
    contenido = PLAN.read_text(encoding="utf-8")

    assert "cargo test" not in contenido
    assert "cargo insta" not in contenido
    assert "python -m pytest -q tests/test_backend_startup_policy.py" in contenido
    assert "python -m pytest -q tests/integration/test_usar_core_contract_full.py" in contenido
    assert "python -m pytest -q tests/test_workflows_yaml.py" in contenido
    assert "python -m pcobra --help" in contenido
