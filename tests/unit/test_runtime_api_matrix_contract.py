from __future__ import annotations

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS
from pcobra.cobra.transpilers.runtime_api_matrix import (
    build_runtime_api_matrix,
    validate_runtime_api_parity_snapshot,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS


PUBLIC_CORELIB_EXTENSION_EXPORTS = {
    "contiene",
    "falso",
    "igual",
    "lanza_error",
    "leer_configuracion",
    "leer_ini",
    "leer_toml",
    "toml_disponible",
    "verdadero",
}

MODULE_ONLY_CORELIB_ALIASES = {
    "ejecutar_proceso",
    "info_registro",
    "leer_json_serializacion",
    "unir_ruta",
}


def test_runtime_api_snapshot_contract_is_up_to_date() -> None:
    validate_runtime_api_parity_snapshot()


def test_runtime_api_matrix_has_all_official_backends_and_python_full() -> None:
    matrix = build_runtime_api_matrix()

    available = matrix["available_api_by_backend"]
    missing = matrix["missing_api_by_backend"]

    assert set(available) == set(OFFICIAL_TARGETS)
    assert set(missing) == set(OFFICIAL_TARGETS)

    assert missing["python"]["global"] == []
    assert missing["python"]["corelibs"] == []
    assert missing["python"]["standard_library"] == []

    for backend in OFFICIAL_TARGETS:
        assert isinstance(available[backend]["global"], list)
        assert isinstance(missing[backend]["global"], list)


def test_python_global_api_includes_ejecutar_comando_async() -> None:
    matrix = build_runtime_api_matrix()

    assert (
        "ejecutar_comando_async"
        in matrix["available_api_by_backend"]["python"]["global"]
    )


def test_python_runtime_preserves_documented_extension_exports_only() -> None:
    matrix = build_runtime_api_matrix()

    python_corelibs = set(matrix["available_api_by_backend"]["python"]["corelibs"])
    assert PUBLIC_CORELIB_EXTENSION_EXPORTS <= python_corelibs
    assert MODULE_ONLY_CORELIB_ALIASES.isdisjoint(matrix["global_api"]["corelibs"])


def test_runtime_public_backend_policy_is_exact() -> None:
    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")
