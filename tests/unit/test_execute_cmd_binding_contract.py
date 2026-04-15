from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand


def test_ejecutar_en_contenedor_resuelve_contrato(monkeypatch):
    import pcobra.cobra.cli.commands.execute_cmd as execute_module

    llamadas: list[str] = []

    def _resolver(target: str):
        llamadas.append(target)

        class _Contrato:
            route = type("R", (), {"value": "javascript_runtime_bridge"})()
            execution_boundary = "Aislado"
            language = "javascript"

        class _Bridge:
            implementation = "javascript_controlled_runtime_bridge"

        return _Contrato(), _Bridge()

    monkeypatch.setattr(execute_module, "_resolver_runtime_binding", _resolver)
    monkeypatch.setattr(
        execute_module.RUNTIME_MANAGER,
        "validate_security_route",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        execute_module.RUNTIME_MANAGER,
        "validate_abi_route",
        lambda *_args, **_kwargs: "1.0",
    )
    monkeypatch.setattr(execute_module, "resolve_docker_backend", lambda value: value)
    monkeypatch.setattr(execute_module, "ejecutar_en_contenedor", lambda _codigo, _backend: "ok")

    assert ExecuteCommand()._ejecutar_en_contenedor("imprimir(1)", "javascript") == 0
    assert llamadas == ["javascript"]
