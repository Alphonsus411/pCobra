import logging
import sys
from types import ModuleType
from unittest.mock import patch

# Crear módulos simulados para evitar dependencias pesadas
fake_yaml = ModuleType("yaml")
fake_yaml.safe_load = lambda *a, **k: {}
sys.modules.setdefault("yaml", fake_yaml)

fake_tsl = ModuleType("tree_sitter_languages")
fake_tsl.get_parser = lambda *a, **k: None
sys.modules.setdefault("tree_sitter_languages", fake_tsl)

fake_rp = ModuleType("RestrictedPython")
fake_rp.compile_restricted = lambda *a, **k: None
fake_rp.safe_builtins = {}
sys.modules.setdefault("RestrictedPython", fake_rp)
eval_mod = ModuleType("Eval")
eval_mod.default_guarded_getitem = lambda seq, key: seq[key]
sys.modules.setdefault("RestrictedPython.Eval", eval_mod)
guards_mod = ModuleType("Guards")
guards_mod.guarded_iter_unpack_sequence = lambda *a, **k: iter([])
guards_mod.guarded_unpack_sequence = lambda *a, **k: []
sys.modules.setdefault("RestrictedPython.Guards", guards_mod)
pc_mod = ModuleType("PrintCollector")
pc_mod.PrintCollector = list
sys.modules.setdefault("RestrictedPython.PrintCollector", pc_mod)

fake_jsonschema = ModuleType("jsonschema")
fake_jsonschema.validate = lambda *a, **k: None
fake_jsonschema.ValidationError = Exception
sys.modules.setdefault("jsonschema", fake_jsonschema)

ipykernel_mod = ModuleType("ipykernel")
kernelbase_mod = ModuleType("ipykernel.kernelbase")
class DummyKernel: ...
kernelbase_mod.Kernel = DummyKernel
sys.modules.setdefault("ipykernel", ipykernel_mod)
sys.modules.setdefault("ipykernel.kernelbase", kernelbase_mod)

requests_mod = ModuleType("requests")
requests_mod.get = lambda *a, **k: None
requests_mod.post = lambda *a, **k: None
sys.modules.setdefault("requests", requests_mod)

from cobra.cli.cli import CliApplication


def test_cli_no_debug(caplog):
    logging.getLogger().handlers.clear()
    app = CliApplication()
    app.initialize()

    with patch.object(app, "execute_command", return_value=0), \
         patch.object(app, "_parse_arguments", side_effect=lambda argv: app.parser.parse_args(argv)), \
         patch("cobra.cli.cli.messages.mostrar_logo"):
        with caplog.at_level(logging.DEBUG):
            ret = app.run([])

    assert ret == 0
    assert logging.getLogger().getEffectiveLevel() == logging.INFO
    assert not any(rec.levelno == logging.DEBUG for rec in caplog.records)
