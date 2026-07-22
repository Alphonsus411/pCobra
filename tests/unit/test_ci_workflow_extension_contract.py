"""Regresiones del contrato de extensiones aplicado a GitHub Actions."""

from pathlib import Path

from scripts.ci import validate_workflow_target_matrix as validator


def _validar(tmp_path: Path, contenido: str) -> list[str]:
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(contenido, encoding="utf-8")

    root_original = validator.ROOT
    try:
        validator.ROOT = tmp_path
        return validator.validate_workflow(workflow, {"python"})
    finally:
        validator.ROOT = root_original


def test_workflow_rechaza_co_como_entrada_de_comando_fuente(tmp_path: Path) -> None:
    errores = _validar(
        tmp_path,
        "jobs:\n  test:\n    steps:\n      - run: cobra ejecutar programa.co\n",
    )

    assert any("debe usar .cobra" in error for error in errores)


def test_workflow_rechaza_co_en_invocacion_python_m_pcobra(tmp_path: Path) -> None:
    errores = _validar(
        tmp_path,
        "jobs:\n  test:\n    steps:\n"
        "      - run: python -m pcobra ejecutar programa.co\n",
    )

    assert any("debe usar .cobra" in error for error in errores)


def test_workflow_acepta_cobra_como_fuente_y_co_como_paquete(tmp_path: Path) -> None:
    errores = _validar(
        tmp_path,
        "jobs:\n  test:\n    steps:\n"
        "      - run: cobra ejecutar programa.cobra\n"
        "      - run: cobra paquete validar dist/demo.co\n",
    )

    assert errores == []


def test_workflow_no_confunde_pytest_con_comando_cobra(tmp_path: Path) -> None:
    errores = _validar(
        tmp_path,
        "jobs:\n  test:\n    steps:\n"
        "      - run: pytest tests/fixtures/paquete_invalido.co\n",
    )

    assert errores == []
