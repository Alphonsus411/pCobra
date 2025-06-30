from types import SimpleNamespace, ModuleType
from unittest.mock import patch
import sys

# Crear un módulo falso para evitar que la importación de sandbox
# requiera RestrictedPython durante las pruebas.
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
sys.modules.setdefault("yaml", ModuleType("yaml"))

from src.cli.commands.interactive_cmd import InteractiveCommand


def _args():
    return SimpleNamespace(seguro=False, validadores_extra=None, sandbox=False, sandbox_docker=None)


def test_interactive_exit():
    cmd = InteractiveCommand()
    with patch('builtins.input', side_effect=['salir']), \
         patch('src.cli.commands.interactive_cmd.InterpretadorCobra') as mock_interp, \
         patch('src.cli.commands.interactive_cmd.validar_dependencias'):
        ret = cmd.run(_args())
    assert ret == 0
    mock_interp.assert_called_once_with(safe_mode=False, extra_validators=None)


def test_interactive_tokens():
    cmd = InteractiveCommand()
    with patch('builtins.input', side_effect=['tokens', 'salir']), \
         patch('src.cli.commands.interactive_cmd.mostrar_info') as mock_info, \
         patch('src.cli.commands.interactive_cmd.validar_dependencias'):
        cmd.run(_args())
    mock_info.assert_any_call('Tokens generados:')


def test_interactive_ast():
    cmd = InteractiveCommand()
    with patch('builtins.input', side_effect=['ast', 'salir']), \
         patch('src.cli.commands.interactive_cmd.mostrar_info') as mock_info, \
         patch('src.cli.commands.interactive_cmd.validar_dependencias'):
        cmd.run(_args())
    mock_info.assert_any_call('AST generado:')
