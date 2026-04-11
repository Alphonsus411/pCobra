from types import SimpleNamespace, ModuleType
from unittest.mock import patch, MagicMock
from io import StringIO
import argparse
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
    return SimpleNamespace(
        seguro=False,
        extra_validators=None,
        sandbox=False,
        sandbox_docker=None,
        ignore_memory_limit=True,
        debug=False,
    )


def test_interactive_exit():
    interp = MagicMock()
    cmd = InteractiveCommand(interp)
    with patch('prompt_toolkit.PromptSession.prompt', side_effect=['salir']), \
         patch('cobra.cli.commands.interactive_cmd.validar_dependencias'):
        ret = cmd.run(_args())
    assert ret == 0


def test_interactive_tokens():
    cmd = InteractiveCommand(MagicMock())
    with patch('prompt_toolkit.PromptSession.prompt', side_effect=['tokens', 'salir']), \
         patch('cobra.cli.commands.interactive_cmd.mostrar_info') as mock_info, \
         patch('cobra.cli.commands.interactive_cmd.validar_dependencias'):
        cmd.run(_args())
    mock_info.assert_any_call('Tokens generados:')


def test_interactive_ast():
    cmd = InteractiveCommand(MagicMock())
    with patch('prompt_toolkit.PromptSession.prompt', side_effect=['ast', 'salir']), \
         patch('cobra.cli.commands.interactive_cmd.mostrar_info') as mock_info, \
         patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('cobra.cli.commands.interactive_cmd.InteractiveCommand.procesar_ast', return_value='AST'):
        cmd.run(_args())
    mock_info.assert_any_call('AST generado:')


def test_interactive_keyboard_interrupt():
    interp = MagicMock()
    cmd = InteractiveCommand(interp)
    with patch('prompt_toolkit.PromptSession.prompt', side_effect=KeyboardInterrupt), \
         patch('cobra.cli.commands.interactive_cmd.mostrar_info') as mock_info, \
         patch('cobra.cli.commands.interactive_cmd.validar_dependencias'):
        ret = cmd.run(_args())
    assert ret == 0
    mock_info.assert_any_call('Saliendo...')


def test_interactive_eof_error():
    interp = MagicMock()
    cmd = InteractiveCommand(interp)
    with patch('prompt_toolkit.PromptSession.prompt', side_effect=EOFError), \
         patch('cobra.cli.commands.interactive_cmd.mostrar_info') as mock_info, \
         patch('cobra.cli.commands.interactive_cmd.validar_dependencias'):
        ret = cmd.run(_args())
    assert ret == 0
    mock_info.assert_any_call('Saliendo...')


def test_interactive_session_persistence():
    inputs = ['x = 5', 'imprimir(x)', 'salir']
    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=inputs), \
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
         patch('prompt_toolkit.PromptSession.prompt', side_effect=['salir']), \
         patch('cobra.cli.commands.interactive_cmd.validar_dependencias'):
        cmd.run(_args())
    mock_expanduser.assert_called_once_with('~/.cobra_history')
    mock_makedirs.assert_called_once_with(str(tmp_path), exist_ok=True)
    mock_history.assert_called_once_with(str(fake_path))


def test_interactive_history_append(tmp_path):
    cmd = InteractiveCommand(MagicMock())
    fake_path = tmp_path / '.cobra_history'

    def fake_prompt(self, *args, **kwargs):
        self.history.append_string('cmd')
        return 'salir'

    with patch('cobra.cli.commands.interactive_cmd.os.path.expanduser', return_value=str(fake_path)), \
         patch('prompt_toolkit.PromptSession.prompt', new=fake_prompt), \
         patch('cobra.cli.commands.interactive_cmd.validar_dependencias'):
        cmd.run(_args())
    assert fake_path.exists()


def test_interactive_help_refleja_politica_de_bloques_y_lineas_blancas():
    cmd = InteractiveCommand(MagicMock())
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    subparser = cmd.register_subparser(subparsers)

    assert subparser.description is not None
    assert 'como máximo 2 líneas en blanco consecutivas' in subparser.description
    assert 'se prohíben bloques vacíos' in subparser.description


def test_interactive_help_incluye_flag_debug():
    cmd = InteractiveCommand(MagicMock())
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    subparser = cmd.register_subparser(subparsers)

    acciones = {action.dest: action for action in subparser._actions}
    assert "debug" in acciones
    assert acciones["debug"].help == "Muestra trazas internas de depuración"


def test_interactive_persist_debug_enabled_en_estado_repl():
    cmd = InteractiveCommand(MagicMock())
    args = _args()
    args.debug = True

    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=['salir']):
        ret = cmd.run(args)

    assert ret == 0
    assert cmd._estado_repl["debug_enabled"] is True


def test_interactive_multiline_si_ejecuta_al_cerrar_bloque():
    inputs = ['si 1 == 1 :', 'imprimir "ok"', 'fin', 'salir']
    cmd = InteractiveCommand(MagicMock())

    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=inputs), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar, \
         patch('cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada', return_value=True):
        ret = cmd.run(_args())

    assert ret == 0
    assert mock_ejecutar.call_count == 1
    codigo_ejecutado, args_ejecutar = mock_ejecutar.call_args[0]
    assert codigo_ejecutado == 'si 1 == 1 :\nimprimir "ok"\nfin'
    assert args_ejecutar is None


def test_interactive_multiline_si_usa_prompt_secundario_y_no_parsea_antes():
    cmd = InteractiveCommand(MagicMock())
    prompts = []
    entradas = iter(['si 1 == 1 :', 'imprimir "ok"', 'fin', 'salir'])

    def _prompt_side_effect(prompt_text):
        prompts.append(prompt_text)
        return next(entradas)

    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=_prompt_side_effect), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar, \
         patch('cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada', return_value=True):
        cmd.run(_args())

    assert prompts[:3] == ['cobra> ', '... ', '... ']
    assert mock_ejecutar.call_count == 1


def test_interactive_multiline_bloque_con_multiples_sentencias_se_ejecuta_igual():
    inputs = ['si 1 == 1 :', 'x = 1', 'imprimir(x)', 'fin', 'salir']
    cmd = InteractiveCommand(MagicMock())

    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=inputs), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar, \
         patch('cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada', return_value=True):
        ret = cmd.run(_args())

    assert ret == 0
    mock_ejecutar.assert_called_once_with('si 1 == 1 :\nx = 1\nimprimir(x)\nfin', None)


def test_interactive_rechaza_fin_sin_bloque_abierto():
    cmd = InteractiveCommand(MagicMock())
    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=['fin', 'salir']), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar, \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        ret = cmd.run(_args())

    assert ret == 0
    assert mock_ejecutar.call_count == 0
    assert "Error: 'fin' sin bloque abierto." in mock_stdout.getvalue()


def test_interactive_rechaza_bloque_vacio():
    cmd = InteractiveCommand(MagicMock())
    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=['si 1 == 1 :', 'fin', 'salir']), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar, \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
         patch('cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada', return_value=True):
        ret = cmd.run(_args())

    assert ret == 0
    assert mock_ejecutar.call_count == 0
    assert "Error: El bloque no puede cerrarse con 'fin' sin sentencias no vacías." in mock_stdout.getvalue()


def test_interactive_lineas_blancas_en_bloque_se_ignoran():
    cmd = InteractiveCommand(MagicMock())
    prompts = []
    entradas = iter(['si 1 == 1 :', '   ', '', 'imprimir "ok"', 'fin', 'salir'])

    def _prompt_side_effect(prompt_text):
        prompts.append(prompt_text)
        return next(entradas)

    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=_prompt_side_effect), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar:
        ret = cmd.run(_args())

    assert ret == 0
    assert prompts[:5] == ['cobra> ', '... ', '... ', '... ', '... ']
    assert mock_ejecutar.call_count == 1
    assert mock_ejecutar.call_args[0][0] == 'si 1 == 1 :\nimprimir "ok"\nfin'


def test_interactive_comando_especial_no_interfiere_con_fin_y_lineas_blanco_en_bloque():
    cmd = InteractiveCommand(MagicMock())
    entradas = ['si 1 == 1 :', 'tokens', '', 'imprimir "ok"', 'fin', 'tokens', 'salir']

    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=entradas), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar, \
         patch.object(cmd, '_procesar_comando_especial', wraps=cmd._procesar_comando_especial) as mock_comando, \
         patch('cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada', return_value=True), \
         patch('cobra.cli.commands.interactive_cmd.mostrar_info'):
        ret = cmd.run(_args())

    assert ret == 0
    mock_ejecutar.assert_called_once_with('si 1 == 1 :\ntokens\nimprimir "ok"\nfin', None)
    lineas_comando_especial = [call.args[0] for call in mock_comando.call_args_list]
    assert lineas_comando_especial.count('tokens') == 1


def test_repl_basico_comparte_validacion_fin_sin_bloque():
    cmd = InteractiveCommand(MagicMock())
    args = _args()
    with patch('builtins.input', side_effect=['fin', 'salir']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar:
        ret = cmd._run_repl_basico(args, validador=None)

    assert ret == 0
    assert mock_ejecutar.call_count == 0
    assert "Error: 'fin' sin bloque abierto." in mock_stdout.getvalue()


def test_interactive_rechaza_exceso_lineas_blanco_consecutivas_en_bloque():
    cmd = InteractiveCommand(MagicMock())
    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=['si 1 == 1 :', '', '', '', 'fin', 'salir']), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar, \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        ret = cmd.run(_args())

    assert ret == 0
    assert mock_ejecutar.call_count == 0
    assert "Error: Máximo de 2 líneas en blanco consecutivas" in mock_stdout.getvalue()


def test_ejecutar_codigo_imprime_booleano_verdadero():
    interp = MagicMock()
    interp.ejecutar_ast.return_value = True
    cmd = InteractiveCommand(interp)

    with patch.object(cmd, 'procesar_ast', return_value=['ast']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        cmd.ejecutar_codigo('codigo', validador=None)

    assert mock_stdout.getvalue().strip() == 'verdadero'


def test_ejecutar_codigo_imprime_booleano_falso():
    interp = MagicMock()
    interp.ejecutar_ast.return_value = False
    cmd = InteractiveCommand(interp)

    with patch.object(cmd, 'procesar_ast', return_value=['ast']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        cmd.ejecutar_codigo('codigo', validador=None)

    assert mock_stdout.getvalue().strip() == 'falso'


def test_ejecutar_codigo_imprime_valor_sin_transformacion():
    cmd_num = InteractiveCommand(MagicMock())
    cmd_num.interpretador.ejecutar_ast.return_value = 123
    with patch.object(cmd_num, 'procesar_ast', return_value=['ast']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout_num:
        cmd_num.ejecutar_codigo('codigo')
    assert mock_stdout_num.getvalue().strip() == '123'

    cmd_txt = InteractiveCommand(MagicMock())
    cmd_txt.interpretador.ejecutar_ast.return_value = 'hola'
    with patch.object(cmd_txt, 'procesar_ast', return_value=['ast']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout_txt:
        cmd_txt.ejecutar_codigo('codigo')
    assert mock_stdout_txt.getvalue().strip() == 'hola'


def test_ejecutar_codigo_no_imprime_cuando_resultado_es_none():
    interp = MagicMock()
    interp.ejecutar_ast.return_value = None
    cmd = InteractiveCommand(interp)

    with patch.object(cmd, 'procesar_ast', return_value=['ast']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        cmd.ejecutar_codigo('codigo', validador=None)

    assert mock_stdout.getvalue() == ''


def test_ejecutar_codigo_traduce_booleano_solo_en_salida_no_en_semantica_interna():
    class _InterpretadorDummy:
        def __init__(self):
            self.ultimo_resultado = None

        def ejecutar_ast(self, ast):
            self.ultimo_resultado = True
            return self.ultimo_resultado

    interp = _InterpretadorDummy()
    cmd = InteractiveCommand(interp)

    with patch.object(cmd, 'procesar_ast', return_value=['ast']), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        cmd.ejecutar_codigo('codigo', validador=None)

    assert mock_stdout.getvalue().strip() == 'verdadero'
    assert interp.ultimo_resultado is True
    assert isinstance(interp.ultimo_resultado, bool)


def test_ejecutar_en_sandbox_arma_script_con_captura_y_booleanos():
    cmd = InteractiveCommand(MagicMock())

    with patch('cobra.cli.commands.interactive_cmd.Lexer') as mock_lexer, \
         patch('cobra.cli.commands.interactive_cmd.Parser') as mock_parser, \
         patch('cobra.cli.commands.interactive_cmd.ejecutar_en_sandbox', return_value='ok') as mock_sandbox, \
         patch('cobra.cli.commands.interactive_cmd.mostrar_info') as mock_info:
        mock_lexer.return_value.tokenizar.return_value = ['TOK']
        mock_parser.return_value.parsear.return_value = ['AST']

        cmd._ejecutar_en_sandbox('imprimir(1)')

    script_enviado = mock_sandbox.call_args.args[0]
    assert '_resultado = _interp.ejecutar_ast(_ast)' in script_enviado
    assert "if _resultado is not None:" in script_enviado
    assert "if isinstance(_resultado, bool):" in script_enviado
    assert "print('verdadero' if _resultado else 'falso')" in script_enviado
    assert 'print(_resultado)' in script_enviado
    mock_info.assert_called_once_with('ok')
