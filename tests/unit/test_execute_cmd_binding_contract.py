from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand


def test_ejecutar_en_contenedor_resuelve_contrato(monkeypatch):
    import pcobra.cobra.cli.commands.execute_cmd as execute_module

    llamadas: list[tuple[str, str]] = []

    class _Contrato:
        route = type("R", (), {"value": "javascript_runtime_bridge"})()
        execution_boundary = "Aislado"
        language = "javascript"

    class _Bridge:
        implementation = "javascript_controlled_runtime_bridge"

    monkeypatch.setattr(
        execute_module.RUNTIME_MANAGER,
        "validate_command_runtime",
        lambda target, **kwargs: llamadas.append((target, kwargs["command"])) or ("1.0", _Contrato(), _Bridge()),
    )
    monkeypatch.setattr(execute_module, "resolve_docker_backend", lambda value: value)
    monkeypatch.setattr(execute_module, "ejecutar_en_contenedor", lambda _codigo, _backend: "ok")

    assert ExecuteCommand()._ejecutar_en_contenedor("imprimir(1)", "javascript") == 0
    assert llamadas == [("javascript", "run")]
