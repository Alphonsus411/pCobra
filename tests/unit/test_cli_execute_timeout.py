import pytest

import pcobra.cobra.cli.services.run_service as run_service


def _agotar_tiempo():
    raise TimeoutError("Tiempo de ejecución agotado")


class _ProcesoBloqueado:
    exitcode = None

    def __init__(self, *, target):
        self.target = target
        self.terminado = False

    def start(self):
        pass

    def join(self, timeout=None):
        self.timeout = timeout

    def is_alive(self):
        return not self.terminado

    def terminate(self):
        self.terminado = True


class _ContextoPosix:
    def Queue(self, *, maxsize):
        return object()

    def Process(self, *, target):
        return _ProcesoBloqueado(target=target)


def test_timeout_posix_sin_iniciar_procesos(monkeypatch):
    servicio = run_service.RunService()
    servicio.execution_timeout = 1
    contexto = _ContextoPosix()

    monkeypatch.setattr(
        run_service.multiprocessing, "get_all_start_methods", lambda: ["fork"]
    )
    monkeypatch.setattr(
        run_service.multiprocessing, "get_context", lambda metodo: contexto
    )

    with pytest.raises(TimeoutError):
        servicio.limitar_recursos(lambda: 0)


def test_timeout_windows_sin_iniciar_procesos(monkeypatch):
    servicio = run_service.RunService()
    servicio.execution_timeout = 1

    monkeypatch.setattr(
        run_service.multiprocessing, "get_all_start_methods", lambda: []
    )

    with pytest.raises(TimeoutError):
        servicio.limitar_recursos(_agotar_tiempo)
