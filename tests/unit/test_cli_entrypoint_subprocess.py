"""Pruebas de extremo a extremo para el punto de entrada de ``cobra``.

Estas pruebas ejecutan comandos reales de la CLI en un subproceso para
verificar que la aplicación principal cargue todos los subcomandos
registrados y que pueda funcionar en un entorno sin las dependencias
opcionales instaladas. Para evitar instalar paquetes pesados se crean
"stubs" temporales que satisfacen las importaciones requeridas por la
CLI completa.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_stub(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).lstrip(), encoding="utf-8")


def _create_stub_environment(tmp_path: Path) -> dict[str, str]:
    stubs_dir = tmp_path / "stubs"
    project_root = tmp_path / "project"
    project_root.mkdir()

    requirements = """\
    numpy==1.0.0
    cobra-lib==0.0.1
    """
    (project_root / "requirements.txt").write_text(dedent(requirements).strip(), encoding="utf-8")

    pyproject = """\
    [project]
    dependencies = [
        "pandas==1.0.0",
        "matplotlib==1.0.0",
    ]
    """
    (project_root / "pyproject.toml").write_text(dedent(pyproject).strip(), encoding="utf-8")

    _write_stub(
        stubs_dir / "yaml.py",
        """
        class YAMLError(Exception):
            pass

        def safe_load(_stream):
            return {}
        """,
    )

    _write_stub(
        stubs_dir / "jsonschema.py",
        """
        class ValidationError(Exception):
            pass

        def validate(*_args, **_kwargs):
            return None
        """,
    )

    _write_stub(
        stubs_dir / "RestrictedPython/__init__.py",
        """
        def compile_restricted(source, filename, mode):
            return compile(source, filename, mode)

        safe_builtins = {}
        """,
    )

    _write_stub(
        stubs_dir / "RestrictedPython/Eval/__init__.py",
        """
        def default_guarded_getitem(*_args, **_kwargs):
            return None

        def default_guarded_getattr(*_args, **_kwargs):
            return None
        """,
    )

    _write_stub(
        stubs_dir / "RestrictedPython/Guards/__init__.py",
        """
        def guarded_iter_unpack_sequence(*_args, **_kwargs):
            return None

        def guarded_unpack_sequence(*_args, **_kwargs):
            return None
        """,
    )

    _write_stub(
        stubs_dir / "RestrictedPython/PrintCollector/__init__.py",
        """
        class PrintCollector:
            def __call__(self):
                return ""
        """,
    )

    _write_stub(
        stubs_dir / "argcomplete/__init__.py",
        """
        def autocomplete(_parser, **_kwargs):
            return None
        """,
    )

    _write_stub(
        stubs_dir / "argcomplete/completers.py",
        """
        class FilesCompleter:
            def __call__(self, *_args, **_kwargs):
                return []

        class DirectoriesCompleter(FilesCompleter):
            pass
        """,
    )

    _write_stub(
        stubs_dir / "prompt_toolkit/__init__.py",
        """
        class PromptSession:
            def __init__(self, *_args, **_kwargs):
                pass

            def prompt(self, *_args, **_kwargs):
                return ""
        """,
    )

    _write_stub(
        stubs_dir / "prompt_toolkit/lexers.py",
        """
        class PygmentsLexer:
            def __init__(self, *_args, **_kwargs):
                pass
        """,
    )

    _write_stub(
        stubs_dir / "prompt_toolkit/history.py",
        """
        class FileHistory:
            def __init__(self, *_args, **_kwargs):
                pass
        """,
    )

    _write_stub(
        stubs_dir / "prompt_toolkit/output/__init__.py",
        """
        class DummyOutput:
            def __init__(self, *_args, **_kwargs):
                pass
        """,
    )

    _write_stub(
        stubs_dir / "prompt_toolkit/output/win32.py",
        """
        class NoConsoleScreenBufferError(Exception):
            pass
        """,
    )

    _write_stub(
        stubs_dir / "filelock.py",
        """
        class FileLock:
            def __init__(self, *_args, **_kwargs):
                self._locked = False

            def __enter__(self):
                self._locked = True
                return self

            def __exit__(self, exc_type, exc, tb):
                self._locked = False
                return False
        """,
    )

    _write_stub(
        stubs_dir / "chardet.py",
        """
        def detect(_data):
            return {"encoding": "utf-8"}
        """,
    )

    _write_stub(
        stubs_dir / "jupyter_kernel.py",
        """
        class CobraKernel:
            pass
        """,
    )

    _write_stub(
        stubs_dir / "pcobra_core_database_stub.py",
        """
        from contextlib import contextmanager


        class DatabaseDependencyError(RuntimeError):
            pass


        class DatabaseKeyError(RuntimeError):
            pass


        @contextmanager
        def get_connection():
            class _DummyConnection:
                def cursor(self):
                    return self

                def execute(self, *_args, **_kwargs):
                    return None

                def fetchone(self):
                    return None

                def commit(self):
                    return None

                def close(self):
                    return None

            yield _DummyConnection()


        def store_ast(*_args, **_kwargs):
            return None


        def load_ast(*_args, **_kwargs):
            return None


        def clear_cache():
            return None


        def save_qualia_state(*_args, **_kwargs):
            return None


        __all__ = [
            "DatabaseDependencyError",
            "DatabaseKeyError",
            "get_connection",
            "store_ast",
            "load_ast",
            "clear_cache",
            "save_qualia_state",
        ]
        """,
    )

    _write_stub(
        stubs_dir / "pcobra_cobra_cli_i18n_stub.py",
        """
        import traceback


        def _(text):
            return text


        def setup_gettext(_lang=None):
            return _


        def format_traceback(exc, _lang=None):
            return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))


        __all__ = ["_", "setup_gettext", "format_traceback"]
        """,
    )

    _write_stub(
        stubs_dir / "sitecustomize.py",
        """
        import importlib.util
        import os
        import sys
        from pathlib import Path

        CODE_ROOT = Path(os.environ.get("PCOBRA_CODE_ROOT", Path.cwd()))
        PROJECT_ROOT = Path(os.environ.get("PCOBRA_PROJECT_ROOT", CODE_ROOT))
        SRC_PATH = CODE_ROOT / "src"
        if str(SRC_PATH) not in sys.path:
            sys.path.insert(0, str(SRC_PATH))

        def _load_stub(name: str, relative: str):
            stub_path = Path(__file__).with_name(relative)
            spec = importlib.util.spec_from_file_location(name, stub_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
                return module
            return None

        database_stub = _load_stub("pcobra.core.database", "pcobra_core_database_stub.py")
        if database_stub is not None:
            try:
                import pcobra.core  # type: ignore

                setattr(pcobra.core, "database", database_stub)
            except Exception:
                pass

        i18n_stub = _load_stub("pcobra.cobra.cli.i18n", "pcobra_cobra_cli_i18n_stub.py")
        if i18n_stub is not None:
            sys.modules["cobra.cli.i18n"] = i18n_stub

        try:
            from cobra.cli.commands import dependencias_cmd

            def _project_root(cls):
                return PROJECT_ROOT

            dependencias_cmd.DependenciasCommand._get_project_root = classmethod(_project_root)
        except Exception:
            pass
        """,
    )

    env = os.environ.copy()
    original_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = os.pathsep.join(
        filter(None, [str(stubs_dir), str(REPO_ROOT / "src"), original_path])
    )
    env["PCOBRA_CODE_ROOT"] = str(REPO_ROOT)
    env["PCOBRA_PROJECT_ROOT"] = str(project_root)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.pop("PYTEST_CURRENT_TEST", None)
    return env


def _run_cli(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "pcobra.cli", *args]
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            check=False,
            timeout=30,
        )
    except subprocess.TimeoutExpired as exc:  # pragma: no cover - diagnóstico
        raise AssertionError(
            "El comando {} se bloqueó tras 30 s.\nstdout acumulado: {!r}\nstderr acumulado: {!r}".format(
                " ".join(cmd), exc.stdout, exc.stderr
            )
        ) from exc


@pytest.mark.timeout(30)
def test_cli_dependencias_listar(tmp_path: Path) -> None:
    env = _create_stub_environment(tmp_path)
    result = _run_cli(["dependencias", "listar"], env)
    assert result.returncode == 0, result.stderr
    stdout = result.stdout
    assert "numpy==1.0.0" in stdout
    assert "pandas==1.0.0" in stdout


@pytest.mark.timeout(30)
def test_cli_agix_help(tmp_path: Path) -> None:
    env = _create_stub_environment(tmp_path)
    result = _run_cli(["agix", "--help"], env)
    assert result.returncode == 0, result.stderr
    stdout = result.stdout
    assert stdout.startswith("usage: cobra agix")
    assert "--peso-precision" in stdout
