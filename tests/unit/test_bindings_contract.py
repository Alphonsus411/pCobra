from pcobra.cobra.bindings.contract import BindingRoute, resolve_binding


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
