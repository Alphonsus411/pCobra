from pcobra.cobra.cli.commands.execute_cmd import ExecuteCommand


def test_ejecutar_en_contenedor_resuelve_contrato(monkeypatch):
    import pcobra.cobra.cli.commands.execute_cmd as execute_module

    llamadas: list[str] = []

    def _resolver(target: str):
        llamadas.append(target)

        class _Contrato:
            route = type("R", (), {"value": "javascript_runtime_bridge"})()
            execution_boundary = "Aislado"

        return _Contrato()

    monkeypatch.setattr(execute_module, "_resolver_contrato_binding", _resolver)
    monkeypatch.setattr(execute_module, "resolve_docker_backend", lambda value: value)
    monkeypatch.setattr(execute_module, "ejecutar_en_contenedor", lambda _codigo, _backend: "ok")

    assert ExecuteCommand()._ejecutar_en_contenedor("imprimir(1)", "javascript") == 0
    assert llamadas == ["javascript"]
