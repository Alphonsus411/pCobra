from __future__ import annotations

import importlib
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Callable

import pytest

# Añade los directorios necesarios al ``PYTHONPATH`` para simplificar los imports
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
PCOBRA_PATH = SRC_ROOT / "pcobra"

for path in (SRC_ROOT, PCOBRA_PATH):
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Carga opcionalmente el paquete principal para mantener compatibilidad
try:  # nosec B001
    import pcobra  # noqa: F401
except Exception:
    pass

if "requests" not in sys.modules:
    fake_requests = ModuleType("requests")
    fake_requests.Response = type("Response", (), {})

    def _fail(*_args, **_kwargs):  # pragma: no cover - solo para pruebas
        raise RuntimeError("requests no disponible en el entorno de pruebas")

    fake_requests.get = _fail
    fake_requests.post = _fail
    sys.modules["requests"] = fake_requests

if "argcomplete" not in sys.modules:
    fake_argcomplete = ModuleType("argcomplete")

    def _noop_autocomplete(_parser=None):  # pragma: no cover - simple stub
        return None

    fake_argcomplete.autocomplete = _noop_autocomplete

    completers = ModuleType("argcomplete.completers")

    class _FakeCompleter:  # pragma: no cover - comportamiento trivial
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def __call__(self, *_args, **_kwargs):
            return []

    completers.FilesCompleter = _FakeCompleter
    completers.DirectoriesCompleter = _FakeCompleter

    fake_argcomplete.completers = completers
    sys.modules["argcomplete"] = fake_argcomplete
    sys.modules["argcomplete.completers"] = completers

if "yaml" not in sys.modules:
    fake_yaml = ModuleType("yaml")

    def _fake_load(*_args, **_kwargs):  # pragma: no cover - stub mínimo
        return {}

    def _fake_dump(*_args, **_kwargs):  # pragma: no cover - stub mínimo
        return ""

    fake_yaml.safe_load = _fake_load
    fake_yaml.safe_dump = _fake_dump
    fake_yaml.dump = _fake_dump
    sys.modules["yaml"] = fake_yaml

if "RestrictedPython" not in sys.modules:
    fake_restricted = ModuleType("RestrictedPython")

    def _fake_compile(source, filename, mode):  # pragma: no cover - stub simple
        return compile(source, filename, mode)

    fake_restricted.compile_restricted = _fake_compile
    fake_restricted.safe_builtins = {}

    eval_module = ModuleType("RestrictedPython.Eval")

    def _guarded_getitem(obj, item):  # pragma: no cover - stub trivial
        return obj[item]

    def _guarded_getattr(obj, attr, default=None):  # pragma: no cover
        return getattr(obj, attr, default)

    eval_module.default_guarded_getitem = _guarded_getitem
    eval_module.default_guarded_getattr = _guarded_getattr

    guards_module = ModuleType("RestrictedPython.Guards")
    guards_module.guarded_iter_unpack_sequence = lambda seq: iter(seq)
    guards_module.guarded_unpack_sequence = lambda seq: list(seq)

    print_module = ModuleType("RestrictedPython.PrintCollector")

    class _FakePrintCollector:  # pragma: no cover - comportamiento mínimo
        def __init__(self, *_args, **_kwargs) -> None:
            self._buffer: list[str] = []

        def __call__(self, *values) -> str:
            if values:
                self._buffer.append(" ".join(map(str, values)))
            return "\n".join(self._buffer)

    print_module.PrintCollector = _FakePrintCollector

    fake_restricted.Eval = eval_module
    fake_restricted.Guards = guards_module
    fake_restricted.PrintCollector = print_module

    sys.modules["RestrictedPython"] = fake_restricted
    sys.modules["RestrictedPython.Eval"] = eval_module
    sys.modules["RestrictedPython.Guards"] = guards_module
    sys.modules["RestrictedPython.PrintCollector"] = print_module

if "jsonschema" not in sys.modules:
    fake_jsonschema = ModuleType("jsonschema")

    class ValidationError(Exception):
        pass

    def _fake_validate(_instance=None, _schema=None, *args, **kwargs):  # pragma: no cover
        return None

    fake_jsonschema.ValidationError = ValidationError
    fake_jsonschema.validate = _fake_validate
    sys.modules["jsonschema"] = fake_jsonschema

if "ipykernel" not in sys.modules:
    fake_ipykernel = ModuleType("ipykernel")
    kernelbase = ModuleType("ipykernel.kernelbase")

    class _FakeKernel:  # pragma: no cover - implementación vacía
        def __init__(self, *_args, **_kwargs) -> None:
            pass

    kernelbase.Kernel = _FakeKernel
    fake_ipykernel.kernelbase = kernelbase
    sys.modules["ipykernel"] = fake_ipykernel
    sys.modules["ipykernel.kernelbase"] = kernelbase

if "prompt_toolkit" not in sys.modules:
    fake_prompt = ModuleType("prompt_toolkit")

    class _FakePromptSession:  # pragma: no cover
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def prompt(self, *_args, **_kwargs) -> str:
            return ""

    fake_prompt.PromptSession = _FakePromptSession

    lexers_module = ModuleType("prompt_toolkit.lexers")

    class _FakePygmentsLexer:  # pragma: no cover
        def __init__(self, *_args, **_kwargs) -> None:
            pass

    lexers_module.PygmentsLexer = _FakePygmentsLexer

    history_module = ModuleType("prompt_toolkit.history")

    class _FakeHistory:  # pragma: no cover
        def __init__(self, *_args, **_kwargs) -> None:
            pass

    history_module.FileHistory = _FakeHistory

    output_module = ModuleType("prompt_toolkit.output")

    class _FakeDummyOutput:  # pragma: no cover
        def __init__(self, *_args, **_kwargs) -> None:
            pass

    output_module.DummyOutput = _FakeDummyOutput

    win32_module = ModuleType("prompt_toolkit.output.win32")

    class NoConsoleScreenBufferError(Exception):
        pass

    win32_module.NoConsoleScreenBufferError = NoConsoleScreenBufferError

    fake_prompt.lexers = lexers_module
    fake_prompt.history = history_module
    fake_prompt.output = output_module
    sys.modules["prompt_toolkit"] = fake_prompt
    sys.modules["prompt_toolkit.lexers"] = lexers_module
    sys.modules["prompt_toolkit.history"] = history_module
    sys.modules["prompt_toolkit.output"] = output_module
    sys.modules["prompt_toolkit.output.win32"] = win32_module

if "filelock" not in sys.modules:
    fake_filelock = ModuleType("filelock")

    class FileLock:  # pragma: no cover - bloqueo simulado
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def acquire(self, *_args, **_kwargs) -> bool:
            return True

        def release(self) -> None:
            return None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

    fake_filelock.FileLock = FileLock
    sys.modules["filelock"] = fake_filelock

if "chardet" not in sys.modules:
    fake_chardet = ModuleType("chardet")

    def _detect(_data):  # pragma: no cover - detección simplificada
        return {"encoding": "utf-8", "confidence": 1.0}

    fake_chardet.detect = _detect
    sys.modules["chardet"] = fake_chardet


# Configuración global mínima para la base de datos durante la importación de módulos
_GLOBAL_DB_DIR = Path(tempfile.gettempdir()) / "pcobra-tests"
_GLOBAL_DB_DIR.mkdir(parents=True, exist_ok=True)
_GLOBAL_DB_PATH = _GLOBAL_DB_DIR / "global.db"

os.environ.setdefault("SQLITE_DB_KEY", "global-test-key")
os.environ.setdefault("COBRA_DB_PATH", str(_GLOBAL_DB_PATH))

database_module = importlib.import_module("pcobra.core.database")


class _GlobalSQLiteStub:
    def __init__(self, db_path: str, cipher_key: str | None = None) -> None:
        self._db_path = db_path

    def get_connection(self):
        conn = sqlite3.connect(self._db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


database_module._load_sqliteplus_class = lambda: _GlobalSQLiteStub  # type: ignore[attr-defined]
database_module._SQLITEPLUS_CLASS = _GlobalSQLiteStub  # type: ignore[attr-defined]
database_module._SQLITEPLUS_INSTANCE = None  # type: ignore[attr-defined]
database_module._TABLES_READY = False  # type: ignore[attr-defined]
sys.modules.setdefault("core.database", database_module)


@pytest.fixture
def ruta_ejemplos() -> Path:
    """Devuelve el directorio donde se guardan los programas ``.cobra`` de prueba."""
    return Path(__file__).resolve().parent / "data"


@pytest.fixture
def cargar_programa(ruta_ejemplos: Path) -> Callable[[str], str]:
    """Carga el contenido de un programa ``.cobra`` por nombre."""

    def _cargar(nombre: str) -> str:
        archivo = ruta_ejemplos / f"{nombre}.cobra"
        return archivo.read_text(encoding="utf-8")

    return _cargar


@pytest.fixture
def codigo_imprimir() -> str:
    """Snippet Cobra que imprime el valor de una variable."""
    return "x = 1\nimprimir(x)"


@pytest.fixture
def codigo_bucle_simple() -> str:
    """Snippet Cobra con un bucle ``mientras`` que imprime valores."""
    return (
        "x = 0\n"
        "mientras x < 2:\n"
        "    imprimir(x)\n"
        "    x = x + 1\n"
        "fin"
    )


@pytest.fixture
def base_datos_temporal(tmp_path_factory, monkeypatch):
    """Configura ``COBRA_DB_PATH`` y ``SQLITE_DB_KEY`` hacia una base temporal."""

    db_dir = tmp_path_factory.mktemp("cobra-db")
    db_path = db_dir / "core.db"

    monkeypatch.setenv("SQLITE_DB_KEY", "testing-key")
    monkeypatch.setenv("COBRA_DB_PATH", str(db_path))

    database_module = importlib.import_module("pcobra.core.database")
    database_module = importlib.reload(database_module)

    class _SQLitePlusStub:
        def __init__(self, db_path: str, cipher_key: str | None = None) -> None:
            self._db_path = db_path

        def get_connection(self):
            conn = sqlite3.connect(self._db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn

    monkeypatch.setattr(
        database_module, "_load_sqliteplus_class", lambda: _SQLitePlusStub
    )
    monkeypatch.setattr(
        database_module, "_SQLITEPLUS_CLASS", _SQLitePlusStub, raising=False
    )
    monkeypatch.setattr(
        database_module, "_SQLITEPLUS_INSTANCE", None, raising=False
    )
    monkeypatch.setattr(
        database_module, "_TABLES_READY", False, raising=False
    )
    monkeypatch.setitem(sys.modules, "core.database", database_module)

    yield db_path

    if db_path.exists():
        db_path.unlink()
    shutil.rmtree(db_dir, ignore_errors=True)
