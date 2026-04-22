from types import SimpleNamespace

import pytest

from pcobra.cobra.cli.services.contracts import (
    ModRequest,
    RunRequest,
    TestRequest as CliTestRequest,
    normalize_mod_request,
    normalize_run_request,
    normalize_test_request,
)


def test_normalize_run_request_defaults_and_aliases() -> None:
    req = normalize_run_request({"file": "main.co"})
    assert req == RunRequest(archivo="main.co")


def test_normalize_test_request_parses_languajes_string() -> None:
    req = normalize_test_request({"archivo": "main.co", "lenguajes": "python,javascript"})
    assert req == CliTestRequest(archivo="main.co", lenguajes=["python", "javascript"])


def test_normalize_mod_request_requires_action_fields() -> None:
    with pytest.raises(ValueError, match="obligatorio"):
        normalize_mod_request({})

    with pytest.raises(ValueError, match="requiere el campo 'ruta'"):
        normalize_mod_request({"accion": "instalar"})

    ok = normalize_mod_request({"action": "search", "name": "math"})
    assert ok == ModRequest(accion="buscar", nombre="math")


def test_normalize_test_request_from_namespace() -> None:
    ns = SimpleNamespace(file="programa.co", langs=["python"])
    req = normalize_test_request(ns)
    assert req.archivo == "programa.co"
    assert req.lenguajes == ["python"]
