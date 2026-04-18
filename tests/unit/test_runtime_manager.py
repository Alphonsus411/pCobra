from pathlib import Path

import pytest

from pcobra.cobra.bindings.contract import BindingRoute
from pcobra.cobra.bindings.runtime_manager import RuntimeManager


def test_runtime_manager_resuelve_bridge_python():
    capabilities, bridge = RuntimeManager().resolve_runtime("python")

    assert capabilities.route is BindingRoute.PYTHON_DIRECT_IMPORT
    assert bridge.implementation == "python_direct_bridge"


def test_runtime_manager_valida_ruta_js_requiere_runtime_gestionado():
    manager = RuntimeManager()

    try:
        manager.validate_security_route("javascript", sandbox=False, containerized=False)
    except ValueError as exc:
        assert "[JavaScript runtime bridge]" in str(exc)
        assert "runtime gestionado" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Se esperaba error de seguridad para JS sin aislamiento")


def test_runtime_manager_valida_abi_por_ruta():
    manager = RuntimeManager()

    assert manager.validate_abi_route("rust", abi_version="1.0") == "1.0"

    try:
        manager.validate_abi_route("rust", abi_version="9.9")
    except ValueError as exc:
        assert "Versiones soportadas" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Se esperaba error ABI por versión no soportada")


def test_runtime_manager_politica_test_exige_sandbox_para_python():
    manager = RuntimeManager()

    try:
        manager.validate_security_route("python", sandbox=False, containerized=False, command="test")
    except ValueError as exc:
        assert "exige sandbox" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Se esperaba error de política test para python")


def test_runtime_manager_validate_command_runtime_retorna_abi_capabilities_y_bridge():
    manager = RuntimeManager()

    abi, capabilities, bridge = manager.validate_command_runtime(
        "rust",
        command="build",
        abi_version="2.0",
    )

    assert abi == "2.0"
    assert capabilities.route is BindingRoute.RUST_COMPILED_FFI
    assert bridge.implementation == "rust_compiled_ffi_bridge"
    assert bridge.internal_only is False


def test_runtime_manager_validate_command_runtime_loguea_contexto_estructurado(caplog):
    manager = RuntimeManager()

    with caplog.at_level("INFO", logger="pcobra.runtime"):
        manager.validate_command_runtime(
            "javascript",
            command="run",
            sandbox=False,
            containerized=True,
        )

    record = next(
        rec for rec in caplog.records if rec.message == "runtime.command.validation.run"
    )
    assert record.command == "run"
    assert record.route == "javascript_runtime_bridge"
    assert record.bridge == "javascript_controlled_runtime_bridge"
    assert record.abi_version == manager.validate_abi_route("javascript")
    assert record.language == "javascript"
    assert record.sandbox is False
    assert record.containerized is True


def test_runtime_manager_negocia_abi_desde_config(monkeypatch, tmp_path: Path):
    manager = RuntimeManager()
    cobra_toml = tmp_path / "cobra.toml"
    cobra_toml.write_text(
        """
[project.abi_by_backend]
rust = "1.0"
""".strip()
    )
    pcobra_toml = tmp_path / "pcobra.toml"
    pcobra_toml.write_text(
        """
[project.backend_abi]
rust = "2.0"
""".strip()
    )

    monkeypatch.setenv("COBRA_TOML", str(cobra_toml))
    monkeypatch.setenv("PCOBRA_CONFIG", str(pcobra_toml))

    # cobra.toml tiene prioridad y define una ABI soportada.
    assert manager.validate_abi_route("rust") == "1.0"


def test_runtime_manager_negocia_abi_actual_por_defecto_javascript(monkeypatch, tmp_path: Path):
    manager = RuntimeManager()
    monkeypatch.setenv("COBRA_TOML", str(tmp_path / "missing-cobra.toml"))
    monkeypatch.setenv("PCOBRA_CONFIG", str(tmp_path / "missing-pcobra.toml"))

    assert manager.validate_abi_route("javascript") == "1.1"


def test_runtime_manager_rechaza_abi_no_compatible_hacia_atras(monkeypatch, tmp_path: Path):
    manager = RuntimeManager()
    cobra_toml = tmp_path / "cobra.toml"
    cobra_toml.write_text(
        """
[project.abi_by_backend]
javascript = "1.2"
""".strip()
    )

    monkeypatch.setenv("COBRA_TOML", str(cobra_toml))
    monkeypatch.delenv("PCOBRA_CONFIG", raising=False)

    try:
        manager.validate_abi_route("javascript")
    except ValueError as exc:
        assert "Versiones soportadas" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Se esperaba rechazo de ABI no soportada")


def test_runtime_manager_abi_contract_lee_abi_by_backend_desde_cobra_toml(monkeypatch, tmp_path: Path):
    manager = RuntimeManager()
    cobra_toml = tmp_path / "cobra.toml"
    cobra_toml.write_text(
        """
[project.abi_by_backend]
python = "1.0"
javascript = "1.0"
rust = "1.1"
""".strip()
    )
    monkeypatch.setenv("COBRA_TOML", str(cobra_toml))
    monkeypatch.delenv("PCOBRA_CONFIG", raising=False)

    assert manager.validate_abi_route("python") == "1.0"
    assert manager.validate_abi_route("javascript") == "1.0"
    assert manager.validate_abi_route("rust") == "1.1"


def test_runtime_manager_abi_contract_lee_backend_abi_desde_pcobra_toml(monkeypatch, tmp_path: Path):
    manager = RuntimeManager()
    pcobra_toml = tmp_path / "pcobra.toml"
    pcobra_toml.write_text(
        """
[project.backend_abi]
javascript = "1.0"
rust = "1.1"
""".strip()
    )
    monkeypatch.setenv("COBRA_TOML", str(tmp_path / "missing-cobra.toml"))
    monkeypatch.setenv("PCOBRA_CONFIG", str(pcobra_toml))

    assert manager.validate_abi_route("javascript") == "1.0"
    assert manager.validate_abi_route("rust") == "1.1"


def test_runtime_manager_rechaza_backend_no_oficial_en_ruta_publica():
    manager = RuntimeManager()

    try:
        manager.resolve_runtime("go")
    except ValueError as exc:
        assert "Lenguaje no permitido en rutas públicas" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Se esperaba rechazo temprano para backend no oficial")


@pytest.mark.parametrize(
    ("language", "command", "sandbox", "containerized", "error"),
    (
        ("python", "test", False, False, "exige sandbox"),
        ("python", "run", False, True, "no puede marcarse como containerizada"),
        ("javascript", "run", False, False, "runtime gestionado"),
        ("javascript", "test", True, False, "exige contenedor"),
        ("rust", "run", True, False, "frontera nativa FFI"),
        ("rust", "test", False, False, "exige contenedor"),
    ),
)
def test_runtime_manager_rechaza_combinaciones_invalidas_por_backend_y_comando(
    language: str,
    command: str,
    sandbox: bool,
    containerized: bool,
    error: str,
):
    manager = RuntimeManager()

    with pytest.raises(ValueError, match=error):
        manager.validate_security_route(
            language,
            command=command,
            sandbox=sandbox,
            containerized=containerized,
        )


@pytest.mark.parametrize(
    ("command", "language", "sandbox", "containerized", "expected_event"),
    (
        ("run", "javascript", False, True, "runtime.command.validation.run"),
        ("build", "rust", False, False, "runtime.command.validation.build"),
        ("test", "python", True, False, "runtime.command.validation.test"),
    ),
)
def test_runtime_manager_evento_uniforme_por_comando(
    caplog,
    command: str,
    language: str,
    sandbox: bool,
    containerized: bool,
    expected_event: str,
):
    manager = RuntimeManager()

    with caplog.at_level("INFO", logger="pcobra.runtime"):
        manager.validate_command_runtime(
            language,
            command=command,
            sandbox=sandbox,
            containerized=containerized,
        )

    record = next(rec for rec in caplog.records if rec.message == expected_event)
    assert record.command == command
    assert record.language == language
    assert record.route
    assert record.bridge
    assert record.abi_version
    assert record.sandbox is sandbox
    assert record.containerized is containerized
