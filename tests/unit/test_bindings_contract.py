from pcobra.cobra.bindings.contract import (
    ABI_POLICY_BY_ROUTE,
    BINDINGS_BY_LANGUAGE,
    OFFICIAL_PUBLIC_LANGUAGES,
    OFFICIAL_PUBLIC_ROUTE_MATRIX,
    ROUTE_OPERATIONAL_LIMITS,
    BindingRoute,
    route_matrix_markdown,
    validate_public_language,
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
        assert "Lenguaje no permitido en rutas públicas" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Se esperaba ValueError para backend no soportado")


def test_contrato_declara_matriz_abi_y_limites_por_cada_ruta():
    for route in BindingRoute:
        assert route in ABI_POLICY_BY_ROUTE
        assert route in ROUTE_OPERATIONAL_LIMITS
        assert ABI_POLICY_BY_ROUTE[route].current in ABI_POLICY_BY_ROUTE[route].supported


def test_contrato_publico_lenguajes_oficiales_no_admite_bindings_extra():
    assert OFFICIAL_PUBLIC_LANGUAGES == ("python", "javascript", "rust")
    assert set(BINDINGS_BY_LANGUAGE) == set(OFFICIAL_PUBLIC_LANGUAGES)
    assert set(OFFICIAL_PUBLIC_ROUTE_MATRIX) == set(OFFICIAL_PUBLIC_LANGUAGES)


def test_validate_public_language_rechaza_lenguaje_no_oficial():
    try:
        validate_public_language("go")
    except ValueError as exc:
        assert "Lenguaje no permitido en rutas públicas" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Se esperaba ValueError para lenguaje no oficial")


def test_route_matrix_markdown_documenta_rutas_oficiales():
    markdown = route_matrix_markdown()

    assert "| Python | direct import bridge |" in markdown
    assert "| JavaScript | runtime bridge |" in markdown
    assert "| Rust | compiled FFI |" in markdown
