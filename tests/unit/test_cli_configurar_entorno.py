import io
import importlib
import logging
import os
import sys
import types


yaml_stub = types.ModuleType("yaml")
yaml_stub.safe_load = lambda _stream: {}


class _YamlError(Exception):
    """Excepción ficticia para simular errores de PyYAML."""


yaml_stub.YAMLError = _YamlError
sys.modules.setdefault("yaml", yaml_stub)

restricted_stub = types.ModuleType("RestrictedPython")
restricted_stub.compile_restricted = lambda source, filename, mode: compile(
    source, filename, mode
)
restricted_stub.safe_builtins = {}

restricted_eval_stub = types.ModuleType("RestrictedPython.Eval")
restricted_eval_stub.default_guarded_getitem = lambda *args, **kwargs: None
restricted_eval_stub.default_guarded_getattr = lambda *args, **kwargs: None

restricted_guards_stub = types.ModuleType("RestrictedPython.Guards")
restricted_guards_stub.guarded_iter_unpack_sequence = lambda *args, **kwargs: None
restricted_guards_stub.guarded_unpack_sequence = lambda *args, **kwargs: None


class _DummyPrintCollector:
    def __call__(self):
        return ""


restricted_print_stub = types.ModuleType("RestrictedPython.PrintCollector")
restricted_print_stub.PrintCollector = _DummyPrintCollector

sys.modules.setdefault("RestrictedPython", restricted_stub)
sys.modules.setdefault("RestrictedPython.Eval", restricted_eval_stub)
sys.modules.setdefault("RestrictedPython.Guards", restricted_guards_stub)
sys.modules.setdefault("RestrictedPython.PrintCollector", restricted_print_stub)

jsonschema_stub = types.ModuleType("jsonschema")


class _JsonSchemaValidationError(Exception):
    """Excepción ficticia de jsonschema."""


jsonschema_stub.ValidationError = _JsonSchemaValidationError
jsonschema_stub.validate = lambda *args, **kwargs: None
sys.modules.setdefault("jsonschema", jsonschema_stub)

from pcobra.cli import configure_encoding, configurar_entorno
import pcobra.cli as cli


def test_configurar_entorno_permiso_denegado(monkeypatch, caplog):
    """Debe registrar un error y continuar cuando .env no se puede leer."""
    monkeypatch.setenv("SQLITE_DB_KEY", "test-key")

    def _raise_permission_error(**_kwargs):
        raise PermissionError("sin permiso")

    monkeypatch.setattr("pcobra.cli.load_dotenv", _raise_permission_error)

    caplog.set_level(logging.ERROR, logger="pcobra.cli")

    configurar_entorno()

    assert "No se pudo acceder al archivo .env" in caplog.text


class _DummyStreamSinReconfigure:
    def __init__(self):
        self.buffer: list[str] = []

    def write(self, text: str) -> int:
        self.buffer.append(text)
        return len(text)

    def getvalue(self) -> str:
        return "".join(self.buffer)


def test_configure_encoding_fallback_no_rompe_sin_reconfigure(monkeypatch):
    out = _DummyStreamSinReconfigure()
    err = _DummyStreamSinReconfigure()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)
    monkeypatch.delenv("PYTHONIOENCODING", raising=False)

    configure_encoding()

    out.write("Salida legible: áéíóú")
    err.write("Error legible: ñ")
    assert out.getvalue() == "Salida legible: áéíóú"
    assert err.getvalue() == "Error legible: ñ"
    assert os.environ["PYTHONIOENCODING"] == "utf-8"


def test_configure_encoding_sobrescribe_pythonioencoding_a_utf8(monkeypatch):
    monkeypatch.setenv("PYTHONIOENCODING", "latin-1")

    configure_encoding()

    assert os.environ["PYTHONIOENCODING"] == "utf-8"


class _DummyStreamConReconfigure(_DummyStreamSinReconfigure):
    def __init__(self):
        super().__init__()
        self.calls: list[dict[str, str]] = []

    def reconfigure(self, *, encoding: str):
        self.calls.append({"encoding": encoding})


def test_configure_encoding_reconfigura_stdout_y_stderr(monkeypatch):
    out = _DummyStreamConReconfigure()
    err = _DummyStreamConReconfigure()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)
    monkeypatch.delenv("PYTHONIOENCODING", raising=False)

    configure_encoding()

    assert out.calls == [{"encoding": "utf-8"}]
    assert err.calls == [{"encoding": "utf-8"}]
    assert os.environ["PYTHONIOENCODING"] == "utf-8"


def test_main_reconfigura_consola_antes_de_logging_y_cli(monkeypatch):
    orden: list[str] = []
    argumentos_recibidos: list[list[str]] = []

    monkeypatch.setenv("COBRA_CLI_COMMAND_PROFILE", "development")
    monkeypatch.setattr(cli, "configure_encoding", lambda: orden.append("utf8"))
    monkeypatch.setattr(cli, "_bootstrap_dev_path_si_opt_in", lambda: orden.append("bootstrap"))
    monkeypatch.setattr(cli, "configure_logging", lambda debug, verbose=0: orden.append("logging"))
    monkeypatch.setattr(cli, "configurar_entorno", lambda: orden.append("entorno"))

    class _DummyApp:
        def run(self, argv):
            argumentos_recibidos.append(argv)
            orden.append("cli")
            return 0

    cli_module = importlib.import_module("pcobra.cobra.cli.cli")
    monkeypatch.setattr(cli_module, "CliApplication", _DummyApp)

    assert cli.main(["comando-ficticio"]) == 0
    assert orden[:3] == ["utf8", "bootstrap", "logging"]
    assert "cli" in orden
    assert argumentos_recibidos == [["comando-ficticio"]]


def test_main_devuelve_exit_code_1_si_falla_configuracion_entorno(monkeypatch, caplog):
    monkeypatch.setattr(cli, "configure_encoding", lambda: None)
    monkeypatch.setattr(cli, "_bootstrap_dev_path_si_opt_in", lambda: None)
    monkeypatch.setattr(cli, "configure_logging", lambda debug, verbose=0: None)
    monkeypatch.setattr(
        cli,
        "configurar_entorno",
        lambda: (_ for _ in ()).throw(RuntimeError("Falta SQLITE_DB_KEY en el entorno")),
    )

    caplog.set_level(logging.ERROR, logger="pcobra.cli")
    assert cli.main(["comando-ficticio"]) == 1
    assert "Falta SQLITE_DB_KEY en el entorno" in caplog.text


def test_configure_encoding_unicode_salida_bytes_utf8(monkeypatch):
    stdout_bytes = io.BytesIO()
    stderr_bytes = io.BytesIO()
    stdout = io.TextIOWrapper(stdout_bytes, encoding="latin-1")
    stderr = io.TextIOWrapper(stderr_bytes, encoding="latin-1")
    monkeypatch.setattr(sys, "stdout", stdout)
    monkeypatch.setattr(sys, "stderr", stderr)
    monkeypatch.delenv("PYTHONIOENCODING", raising=False)

    configure_encoding()
    print("después")
    stdout.flush()

    salida = stdout_bytes.getvalue()
    assert salida == "después\n".encode("utf-8")
    assert salida.decode("utf-8") == "después\n"
