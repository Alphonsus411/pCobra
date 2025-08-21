import pytest

resource = pytest.importorskip("resource")

from core.resource_limits import limitar_memoria_mb, limitar_cpu_segundos


def test_limitar_memoria():
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    limitar_memoria_mb(64)
    new_soft, _ = resource.getrlimit(resource.RLIMIT_AS)
    assert new_soft == 64 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (soft, hard))


def test_limitar_cpu():
    soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
    new_val = 1 if soft in (-1, 0) else soft
    limitar_cpu_segundos(new_val)
    assert resource.getrlimit(resource.RLIMIT_CPU)[0] == new_val
    resource.setrlimit(resource.RLIMIT_CPU, (soft, hard))
