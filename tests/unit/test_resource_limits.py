import json
import pytest

resource = pytest.importorskip("resource")

from pcobra.cobra.cli.execution_pipeline import construir_script_sandbox_canonico
from pcobra.core.sandbox import _run_in_subprocess, ejecutar_en_sandbox
from pcobra.core.resource_limits import limitar_cpu_segundos, limitar_memoria_mb


def test_limites_bajo_nivel_se_aplican_solo_en_subproceso_hijo():
    original_as = resource.getrlimit(resource.RLIMIT_AS)
    original_cpu = resource.getrlimit(resource.RLIMIT_CPU)

    salida = _run_in_subprocess(
        "import json, resource; "
        "print(json.dumps({"
        "'as': resource.getrlimit(resource.RLIMIT_AS), "
        "'cpu': resource.getrlimit(resource.RLIMIT_CPU)"
        "}))",
        memoria_mb=64,
        cpu_segundos=1,
    )

    limites_hijo = json.loads(salida)
    assert tuple(limites_hijo["as"]) == (64 * 1024 * 1024, 64 * 1024 * 1024)
    assert tuple(limites_hijo["cpu"]) == (1, 1)
    assert resource.getrlimit(resource.RLIMIT_AS) == original_as
    assert resource.getrlimit(resource.RLIMIT_CPU) == original_cpu


def test_programa_cobra_con_limites_no_contamina_proceso_anfitrion():
    original_as = resource.getrlimit(resource.RLIMIT_AS)
    original_cpu = resource.getrlimit(resource.RLIMIT_CPU)
    codigo_cobra = 'imprimir "F-01"\n'
    script = construir_script_sandbox_canonico(codigo_cobra)

    salida = ejecutar_en_sandbox(
        script,
        timeout=20,
        memoria_mb=256,
        cpu_segundos=10,
        allow_insecure_fallback=True,
    )

    assert "F-01" in salida
    assert resource.getrlimit(resource.RLIMIT_AS) == original_as
    assert resource.getrlimit(resource.RLIMIT_CPU) == original_cpu


def test_limite_cpu_invalido_rechaza_antes_de_crear_subproceso():
    with pytest.raises(ValueError, match="cpu_segundos"):
        _run_in_subprocess("print('no debe ejecutarse')", cpu_segundos=0)


def test_limitar_memoria_publica_no_contamina_proceso_anfitrion():
    original = resource.getrlimit(resource.RLIMIT_AS)

    limitar_memoria_mb(64)

    assert resource.getrlimit(resource.RLIMIT_AS) == original


def test_limitar_cpu_publica_no_contamina_proceso_anfitrion():
    original = resource.getrlimit(resource.RLIMIT_CPU)

    limitar_cpu_segundos(1)

    assert resource.getrlimit(resource.RLIMIT_CPU) == original


def test_limitar_memoria_publica_rechaza_valores_no_positivos():
    with pytest.raises(ValueError):
        limitar_memoria_mb(0)


def test_limitar_cpu_publica_rechaza_valores_no_positivos():
    with pytest.raises(ValueError):
        limitar_cpu_segundos(0)
