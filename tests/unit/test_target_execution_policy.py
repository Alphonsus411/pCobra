from __future__ import annotations

from argparse import ArgumentTypeError

import pytest

from pcobra.cobra.cli.target_policies import (
    DOCKER_EXECUTABLE_TARGETS,
    OFFICIAL_TRANSPILATION_TARGETS,
    TRANSPILATION_ONLY_TARGETS,
    VERIFICATION_EXECUTABLE_TARGETS,
    build_runtime_capability_message,
    resolve_docker_backend,
)


def test_targets_solo_transpilacion_siguen_siendo_oficiales():
    for target in TRANSPILATION_ONLY_TARGETS:
        assert target in OFFICIAL_TRANSPILATION_TARGETS


@pytest.mark.parametrize("target", TRANSPILATION_ONLY_TARGETS)
def test_resolve_docker_backend_rechaza_targets_oficiales_solo_transpilacion(target: str):
    with pytest.raises(ArgumentTypeError) as exc_info:
        resolve_docker_backend(target)

    mensaje = str(exc_info.value)
    assert target in mensaje
    for runtime_target in DOCKER_EXECUTABLE_TARGETS:
        assert runtime_target in mensaje


def test_verify_runtime_es_subconjunto_explicito_del_runtime_oficial():
    assert set(VERIFICATION_EXECUTABLE_TARGETS).issubset(set(DOCKER_EXECUTABLE_TARGETS))
    assert VERIFICATION_EXECUTABLE_TARGETS == ("python", "rust", "javascript", "cpp")


def test_mensaje_publico_de_runtime_no_promete_sdk_completo_fuera_de_python():
    mensaje = build_runtime_capability_message(
        capability="ejecución en contenedor",
        allowed_targets=DOCKER_EXECUTABLE_TARGETS,
    ).lower()

    assert "no implica" in mensaje
    assert "paridad de ejecución real" in mensaje
    assert "python" in mensaje
    assert "javascript" in mensaje
