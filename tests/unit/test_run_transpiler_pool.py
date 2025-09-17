import sys
import types

import pytest

# Prepara stubs mínimos para los módulos pesados que `compile_cmd` importa.
# Esto evita dependencias innecesarias en las pruebas unitarias.
cobra_transpilers = types.ModuleType("cobra.transpilers")
cobra_transpilers.module_map = types.SimpleNamespace(get_toml_map=lambda: {})
cobra_transpilers.__path__ = []
sys.modules.setdefault("cobra.transpilers", cobra_transpilers)

transpiler_pkg = types.ModuleType("cobra.transpilers.transpiler")
transpiler_pkg.__path__ = []
sys.modules.setdefault("cobra.transpilers.transpiler", transpiler_pkg)

def _stub(mod_name: str, cls_name: str) -> None:
    mod = types.ModuleType(f"cobra.transpilers.transpiler.{mod_name}")
    setattr(mod, cls_name, type(cls_name, (), {}))
    sys.modules[f"cobra.transpilers.transpiler.{mod_name}"] = mod

for name, cls in [
    ("to_asm", "TranspiladorASM"),
    ("to_c", "TranspiladorC"),
    ("to_cobol", "TranspiladorCOBOL"),
    ("to_cpp", "TranspiladorCPP"),
    ("to_fortran", "TranspiladorFortran"),
    ("to_go", "TranspiladorGo"),
    ("to_java", "TranspiladorJava"),
    ("to_kotlin", "TranspiladorKotlin"),
    ("to_js", "TranspiladorJavaScript"),
    ("to_julia", "TranspiladorJulia"),
    ("to_latex", "TranspiladorLatex"),
    ("to_matlab", "TranspiladorMatlab"),
    ("to_mojo", "TranspiladorMojo"),
    ("to_pascal", "TranspiladorPascal"),
    ("to_php", "TranspiladorPHP"),
    ("to_perl", "TranspiladorPerl"),
    ("to_visualbasic", "TranspiladorVisualBasic"),
    ("to_python", "TranspiladorPython"),
    ("to_r", "TranspiladorR"),
    ("to_ruby", "TranspiladorRuby"),
    ("to_rust", "TranspiladorRust"),
    ("to_wasm", "TranspiladorWasm"),
    ("to_swift", "TranspiladorSwift"),
]:
    _stub(name, cls)

# Stubs adicionales requeridos por ``compile_cmd``.
sys.modules.setdefault("cobra.cli.commands.base", types.SimpleNamespace(BaseCommand=object))
sys.modules.setdefault("cobra.cli.i18n", types.SimpleNamespace(_=lambda s: s))
sys.modules.setdefault(
    "cobra.cli.utils.messages",
    types.SimpleNamespace(mostrar_error=lambda *a, **k: None, mostrar_info=lambda *a, **k: None),
)
sys.modules.setdefault("core.ast_cache", types.SimpleNamespace(obtener_ast=lambda code: None))
sys.modules.setdefault(
    "core.sandbox", types.SimpleNamespace(validar_dependencias=lambda *a, **k: None)
)
sys.modules.setdefault(
    "core.semantic_validators",
    types.SimpleNamespace(PrimitivaPeligrosaError=Exception, construir_cadena=lambda: None),
)

# Pre-importa ``cobra.core`` para estabilizar las dependencias internas.
import cobra.core  # noqa: F401

from cobra.cli.commands.compile_cmd import (
    run_transpiler_pool,
    MAX_LANGUAGES,
    PROCESS_TIMEOUT,
)


def dummy_executor(params):
    """Executor de prueba que retorna (lang, resultado)."""
    lang, _ast = params
    return lang, f"resultado_{lang}"


def test_run_transpiler_pool_small_list(monkeypatch):
    """Verifica que se obtenga el retorno correcto para pocos lenguajes."""

    class DummyPool:
        last_timeout = None

        def __init__(self, processes=None):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def map_async(self, func, iterable, chunksize=None):
            class R:
                def __init__(self, data):
                    self._data = data

                def get(self, timeout=None):
                    DummyPool.last_timeout = timeout
                    return self._data

            return R([func(item) for item in iterable])

    import multiprocessing

    monkeypatch.setattr(multiprocessing, "Pool", DummyPool)

    languages = ["python", "js"]
    ast = None
    resultado = run_transpiler_pool(languages, ast, dummy_executor)
    esperado = [(lang, f"resultado_{lang}") for lang in languages]
    assert resultado == esperado
    assert DummyPool.last_timeout == PROCESS_TIMEOUT


def test_run_transpiler_pool_timeout(monkeypatch):
    """Verifica que el timeout se aplique al obtener el resultado."""

    class DummyPool:
        last_timeout = None

        def __init__(self, processes=None):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def map_async(self, func, iterable, chunksize=None):
            class R:
                def get(self, timeout=None):
                    DummyPool.last_timeout = timeout
                    raise multiprocessing.TimeoutError

            return R()

    import multiprocessing

    monkeypatch.setattr(multiprocessing, "Pool", DummyPool)

    languages = ["python"]
    ast = None

    with pytest.raises(multiprocessing.TimeoutError):
        run_transpiler_pool(languages, ast, dummy_executor)

    assert DummyPool.last_timeout == PROCESS_TIMEOUT


def test_run_transpiler_pool_excesive_languages():
    """Verifica que se lance ValueError cuando se excede MAX_LANGUAGES."""
    languages = [f"lang{i}" for i in range(MAX_LANGUAGES + 1)]
    ast = None
    with pytest.raises(ValueError):
        run_transpiler_pool(languages, ast, dummy_executor)
