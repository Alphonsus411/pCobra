from bindings.contract import BindingRoute, resolve_binding


def test_binding_contract_canonical_route_python():
    assert resolve_binding("python").route is BindingRoute.PYTHON_DIRECT_IMPORT
