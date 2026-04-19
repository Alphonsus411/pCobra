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
        assert "runtime gestionado" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Se esperaba error de seguridad para JS sin aislamiento")


def test_runtime_manager_valida_abi_por_ruta():
    manager = RuntimeManager()

    assert manager.validate_abi_route("rust", abi_version="1.0") == "1.0"

    try:
        manager.validate_abi_route("rust", abi_version="2.0")
    except ValueError as exc:
        assert "Versiones soportadas" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Se esperaba error ABI por versión no soportada")


def test_runtime_manager_permite_python_en_contenedor():
    manager = RuntimeManager()

    manager.validate_security_route("python", sandbox=False, containerized=True)
