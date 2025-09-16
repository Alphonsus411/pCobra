import logging
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

from pcobra.cli import configurar_entorno


def test_configurar_entorno_permiso_denegado(monkeypatch, caplog):
    """Debe registrar un error y continuar cuando .env no se puede leer."""

    def _raise_permission_error():
        raise PermissionError("sin permiso")

    monkeypatch.setattr("pcobra.cli.load_dotenv", _raise_permission_error)

    caplog.set_level(logging.ERROR, logger="pcobra.cli")

    configurar_entorno()

    assert "No se pudo acceder al archivo .env" in caplog.text
