import pytest

from pcobra.cobra.architecture.backend_policy import INTERNAL_BACKENDS, PUBLIC_BACKENDS
from pcobra.cobra.architecture.contracts import assert_backend_allowed_for_scope
from pcobra.cobra.config.transpile_targets import ALLOWED_TARGETS
from pcobra.cobra.transpilers.registry import (
    PUBLIC_TRANSPILER_CLASS_PATHS,
    official_transpiler_registry_literal,
    official_transpiler_targets,
)


def test_politica_publica_exacta_tres_backends():
    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")


def test_allowed_targets_deriva_de_public_backends():
    assert ALLOWED_TARGETS is PUBLIC_BACKENDS
    assert ALLOWED_TARGETS == ("python", "javascript", "rust")


def test_registro_publico_transpiladores_expone_exactamente_public_backends():
    assert tuple(PUBLIC_TRANSPILER_CLASS_PATHS) == PUBLIC_BACKENDS
    assert official_transpiler_targets() == PUBLIC_BACKENDS
    assert tuple(official_transpiler_registry_literal()) == PUBLIC_BACKENDS


def test_internal_migration_scope_permite_solo_backends_internos_controlados():
    assert INTERNAL_BACKENDS == ("go", "cpp", "java", "wasm", "asm")

    assert_backend_allowed_for_scope(backend="go", scope="internal_migration")

    with pytest.raises(ValueError, match="Backend no reconocido para migración interna"):
        assert_backend_allowed_for_scope(backend="ruby", scope="internal_migration")
