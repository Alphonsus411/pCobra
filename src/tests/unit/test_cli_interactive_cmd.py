from types import SimpleNamespace, ModuleType
from unittest.mock import patch, MagicMock
from io import StringIO
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
jsonschema_mod = ModuleType("jsonschema")
jsonschema_mod.validate = lambda *a, **k: None
jsonschema_mod.ValidationError = Exception
sys.modules.setdefault("jsonschema", jsonschema_mod)

import cobra.cli
import cobra.cli.commands

from cobra.cli.commands.interactive_cmd import InteractiveCommand
from core.interpreter import InterpretadorCobra


def _args():
    return SimpleNamespace(seguro=False, validadores_extra=None, sandbox=False, sandbox_docker=None)


def test_interactive_exit():
    interp = MagicMock()
    cmd = InteractiveCommand(interp)
    with patch('prompt_toolkit.shortcuts.prompt.PromptSession.prompt', side_effect=['salir']), \
         patch('cobra.cli.commands.interactive_cmd.validar_dependencias'):
        ret = cmd.run(_args())
    assert ret == 0


def test_interactive_tokens():
    cmd = InteractiveCommand(MagicMock())
    with patch('prompt_toolkit.shortcuts.prompt.PromptSession.prompt', side_effect=['tokens', 'salir']), \
         patch('cobra.cli.commands.interactive_cmd.mostrar_info') as mock_info, \
         patch('cobra.cli.commands.interactive_cmd.validar_dependencias'):
        cmd.run(_args())
    mock_info.assert_any_call('Tokens generados:')


def test_interactive_ast():
    cmd = InteractiveCommand(MagicMock())
    with patch('prompt_toolkit.shortcuts.prompt.PromptSession.prompt', side_effect=['ast', 'salir']), \
         patch('cobra.cli.commands.interactive_cmd.mostrar_info') as mock_info, \
         patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('cobra.cli.commands.interactive_cmd.InteractiveCommand.procesar_ast', return_value='AST'):
        cmd.run(_args())
    mock_info.assert_any_call('AST generado:')


def test_interactive_keyboard_interrupt():
    interp = MagicMock()
    cmd = InteractiveCommand(interp)
    with patch('prompt_toolkit.shortcuts.prompt.PromptSession.prompt', side_effect=KeyboardInterrupt), \
         patch('cobra.cli.commands.interactive_cmd.mostrar_info') as mock_info, \
         patch('cobra.cli.commands.interactive_cmd.validar_dependencias'):
        ret = cmd.run(_args())
    assert ret == 0
    mock_info.assert_any_call('Saliendo...')


def test_interactive_eof_error():
    interp = MagicMock()
    cmd = InteractiveCommand(interp)
    with patch('prompt_toolkit.shortcuts.prompt.PromptSession.prompt', side_effect=EOFError), \
         patch('cobra.cli.commands.interactive_cmd.mostrar_info') as mock_info, \
         patch('cobra.cli.commands.interactive_cmd.validar_dependencias'):
        ret = cmd.run(_args())
    assert ret == 0
    mock_info.assert_any_call('Saliendo...')


def test_interactive_session_persistence():
    inputs = ['x = 5', 'imprimir(x)', 'salir']
    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.shortcuts.prompt.PromptSession.prompt', side_effect=inputs), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
         patch('cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada', return_value=True):
        cmd = InteractiveCommand(InterpretadorCobra())
        cmd.run(_args())
    salida = mock_stdout.getvalue().strip().split('\n')
    assert salida[-1] == '5'


def test_interactive_history_setup(tmp_path):
    cmd = InteractiveCommand(MagicMock())
    fake_path = tmp_path / '.cobra_history'
    with patch('cobra.cli.commands.interactive_cmd.os.path.expanduser', return_value=str(fake_path)) as mock_expanduser, \
         patch('cobra.cli.commands.interactive_cmd.os.makedirs') as mock_makedirs, \
         patch('cobra.cli.commands.interactive_cmd.FileHistory') as mock_history, \
         patch('prompt_toolkit.shortcuts.prompt.PromptSession.prompt', side_effect=['salir']), \
         patch('cobra.cli.commands.interactive_cmd.validar_dependencias'):
        cmd.run(_args())
    mock_expanduser.assert_called_once_with('~/.cobra_history')
    mock_makedirs.assert_called_once_with(str(tmp_path), exist_ok=True)
    mock_history.assert_called_once_with(str(fake_path))
