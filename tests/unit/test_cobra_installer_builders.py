from __future__ import annotations

import pytest

from pcobra.cobra_installer import (
    BuildBackend,
    Builder,
    BuilderKind,
    CobraInstallerError,
    LocalPyInstallerBuilder,
    resolve_build_backend,
)


@pytest.mark.parametrize("reserved", ["docker", "vm", "ci", "remote"])
def test_builders_reservados_devuelven_error_claro(reserved: str) -> None:
    with pytest.raises(CobraInstallerError) as exc_info:
        resolve_build_backend(reserved)

    message = str(exc_info.value)
    assert f"{reserved!r}" in message
    assert "arquitectura" in message
    assert "todavía no está implementado" in message
    assert "builder='local'" in message


def test_builder_local_resuelve_backend_pyinstaller() -> None:
    backend = resolve_build_backend(BuilderKind.LOCAL)

    assert isinstance(backend, LocalPyInstallerBuilder)
    assert backend.kind is Builder.LOCAL
    assert isinstance(backend, BuildBackend)
