from __future__ import annotations

import multiprocessing
import sys
from types import SimpleNamespace

import pytest

from pcobra.cobra.cli.services.run_service import RunService
from pcobra.cobra.cli.services.contracts import RunRequest


@pytest.mark.parametrize("extension", [".co", ".txt", ".py"])
def test_run_service_rechaza_archivos_que_no_son_fuente_cobra(
    tmp_path, extension
):
    archivo = tmp_path / f"programa{extension}"
    archivo.write_text('imprimir("no ejecutar")\n', encoding="utf-8")

    with pytest.raises(ValueError, match="paquete Cobra|extensión \\.cobra"):
        RunService().validar_archivo(str(archivo))


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
