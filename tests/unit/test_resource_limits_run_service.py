from __future__ import annotations

import sys

import pytest

from pcobra.cobra.cli.services.run_service import RunService


@pytest.mark.skipif(sys.platform != "linux", reason="resource module is Unix-specific")
def test_run_service_sandbox_con_programa_cobra_no_contamina_anfitrion(monkeypatch):
    import resource

    llamadas_sandbox: list[dict[str, object]] = []

    def fail_setrlimit(*_args, **_kwargs):
        raise AssertionError("RunService no debe aplicar setrlimit en el anfitrión")

    def fake_ejecutar_en_sandbox(_script, **kwargs):
        llamadas_sandbox.append(kwargs)
        return "ok\n"

    monkeypatch.setattr(resource, "setrlimit", fail_setrlimit)
    monkeypatch.setattr(
        "pcobra.cobra.cli.services.run_service.sandbox_module.ejecutar_en_sandbox",
        fake_ejecutar_en_sandbox,
    )

    servicio = RunService()
    rc = servicio.ejecutar_en_sandbox(
        'imprimir("ok")',
        seguro=True,
        extra_validators=None,
        allow_insecure_fallback=True,
    )

    assert rc == 0
    assert llamadas_sandbox
    assert llamadas_sandbox[0]["cpu_segundos"] == servicio.execution_timeout
