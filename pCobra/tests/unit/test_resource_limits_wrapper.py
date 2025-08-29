from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

import core.resource_limits as shared


def cargar_wrapper():
    """Carga el módulo de límites de recursos del paquete cobra-lenguaje."""
    ruta = (
        Path(__file__).resolve().parents[2]
        / "cobra-lenguaje"
        / "src"
        / "core"
        / "resource_limits.py"
    )
    loader = SourceFileLoader("cobra_lenguaje.core.resource_limits", str(ruta))
    spec = spec_from_loader(loader.name, loader)
    module = module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_cobra_lenguaje_reexporta_modulo_compartido():
    wrapper = cargar_wrapper()
    assert wrapper.limitar_memoria_mb is shared.limitar_memoria_mb
    assert wrapper.limitar_cpu_segundos is shared.limitar_cpu_segundos
