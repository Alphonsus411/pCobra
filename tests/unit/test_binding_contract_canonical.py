from bindings.contract import BindingRoute, OFFICIAL_PUBLIC_ROUTE_MATRIX, resolve_binding


def test_binding_contract_canonical_route_python():
    assert resolve_binding("python").route is BindingRoute.PYTHON_DIRECT_IMPORT


def test_binding_contract_canonical_route_javascript():
    assert resolve_binding("javascript").route is BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE


def test_binding_contract_canonical_route_rust():
    assert resolve_binding("rust").route is BindingRoute.RUST_COMPILED_FFI


def test_binding_contract_public_backends_tienen_mapeo_1_a_1_con_matriz_oficial():
    expected = {
        "python": BindingRoute.PYTHON_DIRECT_IMPORT,
        "javascript": BindingRoute.JAVASCRIPT_RUNTIME_BRIDGE,
        "rust": BindingRoute.RUST_COMPILED_FFI,
    }
    assert OFFICIAL_PUBLIC_ROUTE_MATRIX == expected
