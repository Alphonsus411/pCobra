from __future__ import annotations

import importlib.util
from pathlib import Path


_CONFTEST_PATH = Path(__file__).resolve().parents[1] / "conftest.py"
_SPEC = importlib.util.spec_from_file_location("tests_conftest_contract", _CONFTEST_PATH)
assert _SPEC is not None and _SPEC.loader is not None
tests_conftest = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(tests_conftest)


def test_clasifica_directorio_legacy_como_legacy_explicito() -> None:
    assert tests_conftest._marcas_legacy_para_item(
        "tests/legacy/test_obsoleto.py",
        "tests/legacy/test_obsoleto.py::test_obsoleto",
        set(),
    ) == ("legacy",)


def test_clasifica_guardas_legacy_vigentes_como_legacy_contract() -> None:
    assert tests_conftest._marcas_legacy_para_item(
        "tests/unit/test_legacy_backend_lifecycle.py",
        "tests/unit/test_legacy_backend_lifecycle.py::test_legacy_backend_lifecycle_removed",
        set(),
    ) == ("legacy_contract",)


def test_no_clasifica_pruebas_vigentes_sin_legacy() -> None:
    assert (
        tests_conftest._marcas_legacy_para_item(
            "tests/unit/test_usar.py",
            "tests/unit/test_usar.py::test_usar_numero_dos_veces_es_idempotente",
            set(),
        )
        == ()
    )


def test_no_sobrescribe_marca_legacy_explicita() -> None:
    assert tests_conftest._marcas_legacy_para_item(
        "tests/legacy/test_obsoleto.py",
        "tests/legacy/test_obsoleto.py::test_obsoleto",
        {"legacy"},
    ) == ()
