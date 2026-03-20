from __future__ import annotations

import pytest

from pcobra.cobra.cli.target_policies import (
    DOCKER_EXECUTABLE_TARGETS,
    OFFICIAL_TRANSPILATION_TARGETS,
    TRANSPILATION_ONLY_TARGETS,
    VERIFICATION_EXECUTABLE_TARGETS,
    resolve_docker_backend,
)


def test_targets_solo_transpilacion_siguen_siendo_oficiales():
    for target in TRANSPILATION_ONLY_TARGETS:
        assert target in OFFICIAL_TRANSPILATION_TARGETS


@pytest.mark.parametrize("target", TRANSPILATION_ONLY_TARGETS)
def test_resolve_docker_backend_rechaza_targets_oficiales_solo_transpilacion(target: str):
    with pytest.raises(ValueError) as exc_info:
        resolve_docker_backend(target)

    mensaje = str(exc_info.value)
    assert target in mensaje
    for runtime_target in DOCKER_EXECUTABLE_TARGETS:
        assert runtime_target in mensaje


def test_verify_runtime_es_subconjunto_explicito_del_runtime_oficial():
    assert set(VERIFICATION_EXECUTABLE_TARGETS).issubset(set(DOCKER_EXECUTABLE_TARGETS))
    assert VERIFICATION_EXECUTABLE_TARGETS == ("python", "javascript")
