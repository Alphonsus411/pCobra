from pcobra.cobra.bindings.contract import (
    ABI_POLICY_BY_ROUTE,
    ROUTE_OPERATIONAL_LIMITS,
    BindingRoute,
    resolve_binding,
)


def test_resolve_binding_define_tres_rutas_contractuales():
    assert resolve_binding("python").route is BindingRoute.PYTHON_DIRECT_IMPORT
    assert resolve_binding("javascript").route is BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE
    assert resolve_binding("rust").route is BindingRoute.RUST_COMPILED_FFI


def test_resolve_binding_falla_en_backend_no_soportado():
    try:
        resolve_binding("go")
    except ValueError as exc:
        assert "Lenguajes soportados" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Se esperaba ValueError para backend no soportado")


def test_contrato_declara_matriz_abi_y_limites_por_cada_ruta():
    for route in BindingRoute:
        assert route in ABI_POLICY_BY_ROUTE
        assert route in ROUTE_OPERATIONAL_LIMITS
        assert ABI_POLICY_BY_ROUTE[route].current in ABI_POLICY_BY_ROUTE[route].supported
