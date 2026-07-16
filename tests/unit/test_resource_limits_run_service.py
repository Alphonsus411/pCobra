from __future__ import annotations

import multiprocessing
import sys
import time
from types import SimpleNamespace

import pytest

from pcobra.cobra.cli.services.run_service import RunService
from pcobra.cobra.cli.services.contracts import RunRequest


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


def test_run_service_run_sandbox_delega_en_metodo_con_main_file(
    monkeypatch, tmp_path
):
    archivo = tmp_path / "programa.cobra"
    archivo.write_text('imprimir("ok")\n', encoding="utf-8")
    servicio = RunService()
    capturado: dict[str, object] = {}

    monkeypatch.setattr(
        "pcobra.cobra.cli.services.run_service.RUNTIME_MANAGER.validate_command_runtime",
        lambda *_args, **_kwargs: ("1.0", SimpleNamespace(language="python"), object()),
    )
    monkeypatch.setattr(
        "pcobra.cobra.cli.services.run_service.sandbox_module.validar_dependencias",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(servicio, "limitar_recursos", lambda funcion: funcion())

    def fake_ejecutar_en_sandbox(
        codigo,
        seguro,
        extra_validators,
        *,
        main_file=None,
        allow_insecure_fallback=False,
    ):
        capturado.update(
            {
                "codigo": codigo,
                "seguro": seguro,
                "extra_validators": extra_validators,
                "main_file": main_file,
                "allow_insecure_fallback": allow_insecure_fallback,
            }
        )
        return 0

    monkeypatch.setattr(servicio, "ejecutar_en_sandbox", fake_ejecutar_en_sandbox)

    rc = servicio.run(RunRequest(archivo=str(archivo), sandbox=True))

    assert rc == 0
    assert capturado["codigo"] == 'imprimir("ok")\n'
    assert capturado["main_file"] == archivo.resolve()


@pytest.mark.skipif(
    "fork" not in multiprocessing.get_all_start_methods(),
    reason="requiere fork para aislar la ejecución normal sin serializar closures",
)
def test_run_service_limitar_recursos_corta_ejecucion_normal_sin_setrlimit(
    monkeypatch,
):
    import resource

    def fail_setrlimit(*_args, **_kwargs):
        raise AssertionError("RunService no debe aplicar setrlimit en el anfitrión")

    monkeypatch.setattr(resource, "setrlimit", fail_setrlimit)
    servicio = RunService()
    servicio.execution_timeout = 0.2

    def bucle_infinito():
        while True:
            time.sleep(0.01)

    inicio = time.monotonic()
    with pytest.raises(TimeoutError, match="Tiempo de ejecución agotado"):
        servicio.limitar_recursos(bucle_infinito)

    assert time.monotonic() - inicio < 3


@pytest.mark.skipif(
    "fork" not in multiprocessing.get_all_start_methods(),
    reason="requiere fork para aislar la ejecución normal sin serializar closures",
)
def test_run_service_limitar_recursos_devuelve_codigo_de_ejecucion_normal():
    servicio = RunService()
    servicio.execution_timeout = 2

    assert servicio.limitar_recursos(lambda: 7) == 7
