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
yaml_mod = ModuleType("yaml")
yaml_mod.safe_load = lambda *a, **k: {}
sys.modules.setdefault("yaml", yaml_mod)
tsl_mod = ModuleType("tree_sitter_languages")
tsl_mod.get_parser = lambda *a, **k: None
sys.modules.setdefault("tree_sitter_languages", tsl_mod)

import cli
import cli.commands
sys.modules.setdefault("src.cli", cli)
sys.modules.setdefault("src.cli.commands", cli.commands)

from cli.commands.interactive_cmd import InteractiveCommand


def _args():
    return SimpleNamespace(seguro=False, validadores_extra=None, sandbox=False, sandbox_docker=None)


def test_interactive_exit():
    cmd = InteractiveCommand()
    with patch('builtins.input', side_effect=['salir']), \
         patch('cli.commands.interactive_cmd.InterpretadorCobra') as mock_interp, \
         patch('cli.commands.interactive_cmd.validar_dependencias'):
        ret = cmd.run(_args())
    assert ret == 0
    mock_interp.assert_called_once_with(safe_mode=False, extra_validators=None)


def test_interactive_tokens():
    cmd = InteractiveCommand()
    with patch('builtins.input', side_effect=['tokens', 'salir']), \
         patch('cli.commands.interactive_cmd.mostrar_info') as mock_info, \
         patch('cli.commands.interactive_cmd.validar_dependencias'):
        cmd.run(_args())
    mock_info.assert_any_call('Tokens generados:')


def test_interactive_ast():
    cmd = InteractiveCommand()
    with patch('builtins.input', side_effect=['ast', 'salir']), \
         patch('cli.commands.interactive_cmd.mostrar_info') as mock_info, \
         patch('cli.commands.interactive_cmd.validar_dependencias'):
        cmd.run(_args())
    mock_info.assert_any_call('AST generado:')


def test_interactive_keyboard_interrupt():
    cmd = InteractiveCommand()
    with patch('builtins.input', side_effect=KeyboardInterrupt), \
         patch('cli.commands.interactive_cmd.InterpretadorCobra') as mock_interp, \
         patch('cli.commands.interactive_cmd.mostrar_info') as mock_info, \
         patch('cli.commands.interactive_cmd.validar_dependencias'):
        ret = cmd.run(_args())
    assert ret == 0
    mock_interp.assert_called_once_with(safe_mode=False, extra_validators=None)
    mock_info.assert_any_call('Saliendo...')


def test_interactive_eof_error():
    cmd = InteractiveCommand()
    with patch('builtins.input', side_effect=EOFError), \
         patch('cli.commands.interactive_cmd.InterpretadorCobra') as mock_interp, \
         patch('cli.commands.interactive_cmd.mostrar_info') as mock_info, \
         patch('cli.commands.interactive_cmd.validar_dependencias'):
        ret = cmd.run(_args())
    assert ret == 0
    mock_interp.assert_called_once_with(safe_mode=False, extra_validators=None)
    mock_info.assert_any_call('Saliendo...')
