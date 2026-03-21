import time
from argparse import Namespace

import pytest

import sys
import types

import cobra.core.ast_nodes as ast_nodes

# Stubs dinámicos para cualquier nodo AST que se solicite y no exista.
def _missing_node(name):  # pragma: no cover - utilidad de pruebas
    cls = type(name, (), {})
    setattr(ast_nodes, name, cls)
    return cls

def __getattr__(name):  # pragma: no cover - se usa solo en tests
    if name.startswith("Nodo"):
        return _missing_node(name)
    raise AttributeError(name)

ast_nodes.__getattr__ = __getattr__

dummy_transpilers = {
    "asm": "TranspiladorASM",
    "cpp": "TranspiladorCPP",
    "go": "TranspiladorGo",
    "java": "TranspiladorJava",
    "javascript": "TranspiladorJavaScript",
    "python": "TranspiladorPython",
    "rust": "TranspiladorRust",
    "wasm": "TranspiladorWasm",
}

_MODULE_SUFFIX_BY_TARGET = {
    "javascript": "js",
}

for target, class_name in dummy_transpilers.items():
    module_suffix = _MODULE_SUFFIX_BY_TARGET.get(target, target)
    mod_name = f"cobra.transpilers.transpiler.to_{module_suffix}"
    if mod_name not in sys.modules:
        module = types.ModuleType(mod_name)
        setattr(module, class_name, type(class_name, (), {"generate_code": lambda self, ast: ""}))
        sys.modules[mod_name] = module

from cobra.cli.commands.compile_cmd import CompileCommand
from core.cobra_config import tiempo_max_transpilacion


@pytest.mark.performance

def test_transpile_time(tmp_path, monkeypatch):
    """Verifica que la transpilación de múltiples archivos se realiza rápidamente."""
    # Evita cargas de dependencias externas en la transpilación
    monkeypatch.setattr(
        "cobra.cli.commands.compile_cmd.module_map.get_toml_map", lambda: {}
    )

    num_archivos = 5
    archivos = []
    for i in range(num_archivos):
        archivo = tmp_path / f"archivo_{i}.co"
        archivo.write_text("imprimir('hola')\n", encoding="utf-8")
        archivos.append(archivo)

    cmd = CompileCommand()

    inicio = time.perf_counter()
    for archivo in archivos:
        cmd.run(Namespace(archivo=str(archivo), tipo="python", backend=None, tipos=None))
    total = time.perf_counter() - inicio

    umbral = tiempo_max_transpilacion()
    assert (
        total < umbral
    ), f"La transpilación tomó {total:.2f}s y excede el máximo permitido de {umbral:.2f}s"
