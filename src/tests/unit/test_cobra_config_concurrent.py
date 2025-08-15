import threading
import time
import core.cobra_config as cobra_config
from core.cobra_config import cargar_configuracion


def test_cargar_configuracion_concurrente(tmp_path, monkeypatch):
    cfg = tmp_path / "cfg.toml"
    cfg.write_text("valor = 1\n")
    cargar_configuracion.cache_clear()

    original_load = cobra_config.tomli.load

    def slow_load(f):
        time.sleep(0.05)
        return original_load(f)

    monkeypatch.setattr(cobra_config.tomli, "load", slow_load)

    resultados: list[dict | None] = [None] * 10

    def worker(i: int) -> None:
        resultados[i] = cargar_configuracion(str(cfg))

    hilos = [threading.Thread(target=worker, args=(i,)) for i in range(len(resultados))]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()

    assert all(r == resultados[0] for r in resultados)
    assert cargar_configuracion.cache_info().currsize == 1
