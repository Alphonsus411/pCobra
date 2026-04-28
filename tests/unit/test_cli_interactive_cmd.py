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

from cobra.cli.commands.interactive_cmd import InteractiveCommand, format_user_error
from cobra.core import ParserError, LexerError
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
    inputs = ['var x = 5', 'imprimir(x)', 'salir']
    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=inputs), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
         patch('cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada', return_value=True):
        cmd = InteractiveCommand(InterpretadorCobra())
        cmd.run(_args())
    salida = mock_stdout.getvalue().strip().split('\n')
    assert salida[-1] == '5'


def test_interactive_session_persistence_reutiliza_misma_instancia_en_toda_la_sesion():
    inputs = ['var x = 10', 'var y = x * 2', 'imprimir(y)', 'salir']
    cmd = InteractiveCommand(InterpretadorCobra())
    interpretador_sesion = cmd.interpretador

    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=inputs), \
         patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        ret = cmd.run(_args())

    salida = mock_stdout.getvalue()
    assert ret == 0
    assert cmd.interpretador is interpretador_sesion
    assert cmd._interpretador_sesion is interpretador_sesion
    assert '20' in salida
    assert 'Variable no declarada: _cse0' not in salida


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


def test_interactive_help_no_define_flag_debug_local():
    cmd = InteractiveCommand(MagicMock())
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    subparser = cmd.register_subparser(subparsers)

    acciones = {action.dest: action for action in subparser._actions}
    assert "debug" not in acciones


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
    inputs = ['si verdadero:', 'imprimir "ok"', 'fin', 'salir']
    cmd = InteractiveCommand(MagicMock())

    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=inputs), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar, \
         patch('cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada', return_value=True):
        ret = cmd.run(_args())

    assert ret == 0
    assert mock_ejecutar.call_count == 1
    codigo_ejecutado, args_ejecutar = mock_ejecutar.call_args[0]
    assert codigo_ejecutado == 'si verdadero:\nimprimir "ok"\nfin'
    assert args_ejecutar is None


def test_interactive_multiline_si_usa_prompt_secundario_y_no_parsea_antes():
    cmd = InteractiveCommand(MagicMock())
    prompts = []
    entradas = iter(['si verdadero:', 'imprimir "ok"', 'fin', 'salir'])

    def _prompt_side_effect(prompt_text):
        prompts.append(prompt_text)
        return next(entradas)

    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=_prompt_side_effect), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar, \
         patch('cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada', return_value=True):
        cmd.run(_args())

    assert prompts[:3] == ['>>> ', '... ', '... ']
    assert mock_ejecutar.call_count == 1


def test_interactive_multiline_bloque_con_multiples_sentencias_se_ejecuta_igual():
    inputs = ['si verdadero:', 'var x = 1', 'imprimir(x)', 'fin', 'salir']
    cmd = InteractiveCommand(MagicMock())

    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=inputs), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar, \
         patch('cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada', return_value=True):
        ret = cmd.run(_args())

    assert ret == 0
    mock_ejecutar.assert_called_once_with('si verdadero:\nvar x = 1\nimprimir(x)\nfin', None)


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
         patch('prompt_toolkit.PromptSession.prompt', side_effect=['si verdadero:', 'fin', 'salir']), \
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
    entradas = iter(['si verdadero:', '   ', '', 'imprimir "ok"', 'fin', 'salir'])

    def _prompt_side_effect(prompt_text):
        prompts.append(prompt_text)
        return next(entradas)

    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=_prompt_side_effect), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar:
        ret = cmd.run(_args())

    assert ret == 0
    assert prompts[:5] == ['>>> ', '... ', '... ', '... ', '... ']
    assert mock_ejecutar.call_count == 1
    assert mock_ejecutar.call_args[0][0] == 'si verdadero:\nimprimir "ok"\nfin'


def test_interactive_comando_especial_no_interfiere_con_fin_y_lineas_blanco_en_bloque():
    cmd = InteractiveCommand(MagicMock())
    entradas = ['si verdadero:', 'tokens', '', 'imprimir "ok"', 'fin', 'tokens', 'salir']

    with patch('cobra.cli.commands.interactive_cmd.validar_dependencias'), \
         patch('prompt_toolkit.PromptSession.prompt', side_effect=entradas), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar, \
         patch.object(cmd, '_procesar_comando_especial', wraps=cmd._procesar_comando_especial) as mock_comando, \
         patch('cobra.cli.commands.interactive_cmd.InteractiveCommand.validar_entrada', return_value=True), \
         patch('cobra.cli.commands.interactive_cmd.mostrar_info'):
        ret = cmd.run(_args())

    assert ret == 0
    mock_ejecutar.assert_called_once_with('si verdadero:\ntokens\nimprimir "ok"\nfin', None)
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
         patch('prompt_toolkit.PromptSession.prompt', side_effect=['si verdadero:', '', '', '', 'fin', 'salir']), \
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


def test_ejecutar_codigo_intenta_fallback_para_expresion_top_level_no_soportada():
    cmd = InteractiveCommand(MagicMock())
    setup = SimpleNamespace(
        interpretador=cmd.interpretador,
        safe_mode=cmd._seguro_repl,
        validadores_extra=cmd._extra_validators_repl,
    )
    NodoOperacionBinaria = type("NodoOperacionBinaria", (), {})
    ast_expr = [NodoOperacionBinaria()]
    resultado = SimpleNamespace(ast=ast_expr, resultado=None)
    llamadas = []

    def _pipeline_fake(pipeline_input, analizar_codigo_fn):
        llamadas.append(pipeline_input.codigo)
        if pipeline_input.codigo == "1 + 2":
            raise ValueError("Nodo no soportado: <class 'pcobra.core.ast_nodes.NodoOperacionBinaria'>")
        if pipeline_input.codigo == "imprimir(1 + 2)":
            return setup, resultado
        raise AssertionError(f"Código inesperado: {pipeline_input.codigo}")

    with patch(
        "cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo",
        return_value=ast_expr,
    ), patch(
        "cobra.cli.commands.interactive_cmd.ejecutar_pipeline_explicito",
        side_effect=_pipeline_fake,
    ):
        cmd.ejecutar_codigo("1 + 2")

    assert llamadas == ["1 + 2", "imprimir(1 + 2)"]


def test_ejecutar_codigo_prioriza_error_original_cuando_fallback_tambien_falla():
    cmd = InteractiveCommand(MagicMock())
    NodoOperacionBinaria = type("NodoOperacionBinaria", (), {})
    ast_expr = [NodoOperacionBinaria()]
    llamadas = []
    error_original = "Nodo no soportado: <class 'pcobra.core.ast_nodes.NodoOperacionBinaria'>"
    error_fallback = "falló fallback al envolver en imprimir(...)"

    def _pipeline_fake(pipeline_input, analizar_codigo_fn):
        llamadas.append(pipeline_input.codigo)
        if pipeline_input.codigo == "1 + 2":
            raise ValueError(error_original)
        if pipeline_input.codigo == "imprimir(1 + 2)":
            raise RuntimeError(error_fallback)
        raise AssertionError(f"Código inesperado: {pipeline_input.codigo}")

    with patch(
        "cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo",
        return_value=ast_expr,
    ), patch(
        "cobra.cli.commands.interactive_cmd.ejecutar_pipeline_explicito",
        side_effect=_pipeline_fake,
    ):
        try:
            cmd.ejecutar_codigo("1 + 2")
            assert False, "Se esperaba excepción"
        except ValueError as err:
            assert str(err) == error_original
            assert error_fallback not in str(err)

    assert llamadas == ["1 + 2", "imprimir(1 + 2)"]


def test_ejecutar_codigo_no_intenta_fallback_si_no_es_expresion_top_level():
    cmd = InteractiveCommand(MagicMock())
    NodoAsignacion = type("NodoAsignacion", (), {})
    ast_stmt = [NodoAsignacion()]

    with patch(
        "cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo",
        return_value=ast_stmt,
    ), patch(
        "cobra.cli.commands.interactive_cmd.ejecutar_pipeline_explicito",
        side_effect=ValueError(
            "Nodo no soportado: <class 'pcobra.core.ast_nodes.NodoAsignacion'>"
        ),
    ) as mock_pipeline:
        try:
            cmd.ejecutar_codigo("var x = 1")
            assert False, "Se esperaba excepción"
        except ValueError as err:
            assert "Nodo no soportado" in str(err)

    assert mock_pipeline.call_count == 1


def test_es_nodo_control_sin_echo_repl_reconoce_alias_si_y_mientras_por_nombre():
    cmd = InteractiveCommand(MagicMock())

    NodoSi = type("NodoSi", (), {})
    NodoMientras = type("NodoMientras", (), {})

    assert cmd._es_nodo_control_sin_echo_repl(NodoSi()) is True
    assert cmd._es_nodo_control_sin_echo_repl(NodoMientras()) is True


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


def test_ejecutar_ast_en_repl_ejecuta_nodo_a_nodo_y_no_batch_ejecutar_ast():
    class _NodoDummy:
        def __init__(self, nombre):
            self.nombre = nombre

        def aceptar(self, _validador):
            return None

    class _InterpretadorDummy:
        def __init__(self):
            self.nodos_ejecutados = []

        def ejecutar_ast(self, _ast):
            raise AssertionError("REPL normal no debe usar ejecutar_ast batch")

        def ejecutar_nodo(self, nodo):
            self.nodos_ejecutados.append(nodo.nombre)
            return None if nodo.nombre == "n1" else 20

    interp = _InterpretadorDummy()
    cmd = InteractiveCommand(interp)
    ast_dummy = [_NodoDummy("n1"), _NodoDummy("n2")]

    with patch(
        "cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo",
        return_value=ast_dummy,
    ):
        ast, resultado = cmd._ejecutar_ast_en_repl("var y = x * 2")

    assert ast == ast_dummy
    assert interp.nodos_ejecutados == ["n1", "n2"]
    assert resultado == 20


def test_parsear_y_ejecutar_codigo_repl_restaurar_interpretador_de_sesion():
    cmd = InteractiveCommand(MagicMock(name="interp_sesion"))
    cmd._interpretador_sesion = cmd.interpretador
    cmd.interpretador = MagicMock(name="interp_temporal")

    with patch('cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo'), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar:
        cmd.parsear_y_ejecutar_codigo_repl("imprimir(1)")

    assert cmd.interpretador is cmd._interpretador_sesion
    mock_ejecutar.assert_called_once_with("imprimir(1)")


def test_parsear_y_ejecutar_codigo_repl_no_invoca_pipeline_explicito_en_ruta_normal():
    cmd = InteractiveCommand(MagicMock())

    with patch(
        "cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo",
        return_value=[],
    ) as mock_prevalidar, patch.object(
        cmd,
        "ejecutar_codigo",
    ) as mock_ejecutar, patch(
        "pcobra.cobra.cli.execution_pipeline.ejecutar_pipeline_explicito",
        side_effect=AssertionError("ruta normal no debe invocar pipeline explícito"),
    ) as mock_pipeline:
        cmd.parsear_y_ejecutar_codigo_repl("imprimir(1)")

    mock_prevalidar.assert_called_once_with("imprimir(1)")
    mock_ejecutar.assert_called_once_with("imprimir(1)")
    assert mock_pipeline.call_count == 0


def test_ejecutar_en_sandbox_arma_script_con_captura_y_booleanos():
    cmd = InteractiveCommand(MagicMock())
    cmd._seguro_repl = False
    cmd._extra_validators_repl = ["validador.py"]

    with patch('cobra.cli.commands.interactive_cmd.Lexer') as mock_lexer, \
         patch('cobra.cli.commands.interactive_cmd.Parser') as mock_parser, \
         patch('cobra.cli.commands.interactive_cmd.ejecutar_en_sandbox', return_value='ok') as mock_sandbox, \
         patch('cobra.cli.commands.interactive_cmd.mostrar_info') as mock_info:
        mock_lexer.return_value.tokenizar.return_value = ['TOK']
        mock_parser.return_value.parsear.return_value = ['AST']

        cmd._ejecutar_en_sandbox('imprimir(1)')

    script_enviado = mock_sandbox.call_args.args[0]
    assert "safe_mode=False" in script_enviado
    assert "extra_validators=['validador.py']" in script_enviado
    assert '_resultado = _interp.ejecutar_ast(_ast)' in script_enviado
    assert "if _resultado is not None:" in script_enviado
    assert "if isinstance(_resultado, bool):" in script_enviado
    assert "print('verdadero' if _resultado else 'falso')" in script_enviado
    assert 'print(_resultado)' in script_enviado
    mock_info.assert_called_once_with('ok')


def test_ejecutar_en_sandbox_invoca_pipeline_explicito_solo_para_setup():
    cmd = InteractiveCommand(MagicMock(name="interp_original"))
    cmd._seguro_repl = False
    cmd._extra_validators_repl = ["extra_repl.py"]
    setup = SimpleNamespace(
        interpretador=MagicMock(name="interp_setup"),
        safe_mode=True,
        validadores_extra=["normalizado.py"],
    )

    with patch(
        "pcobra.cobra.cli.execution_pipeline.ejecutar_pipeline_explicito",
        return_value=(setup, SimpleNamespace()),
    ) as mock_pipeline, patch(
        "cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo",
        return_value=[],
    ) as mock_prevalidar, patch(
        "cobra.cli.commands.interactive_cmd.construir_script_sandbox_canonico",
        return_value="SCRIPT",
    ) as mock_script, patch(
        "cobra.cli.commands.interactive_cmd.ejecutar_en_sandbox",
        return_value=None,
    ) as mock_sandbox:
        cmd._ejecutar_en_sandbox("imprimir(7)")

    pipeline_input = mock_pipeline.call_args.args[0]
    assert pipeline_input.codigo == ""
    assert pipeline_input.safe_mode is False
    assert pipeline_input.extra_validators == ["extra_repl.py"]
    assert pipeline_input.interpretador is not None
    mock_prevalidar.assert_called_once_with("imprimir(7)")
    mock_script.assert_called_once_with(
        "imprimir(7)",
        safe_mode=True,
        extra_validators=["normalizado.py"],
        imprimir_resultado=True,
    )
    mock_sandbox.assert_called_once_with(
        "SCRIPT",
        allow_insecure_fallback=False,
    )
    assert cmd.interpretador is setup.interpretador
    assert cmd._seguro_repl is True
    assert cmd._extra_validators_repl == ["normalizado.py"]


def test_run_repl_loop_pasa_estado_repl_a_ejecucion_sandbox():
    cmd = InteractiveCommand(MagicMock())
    cmd._seguro_repl = False
    cmd._extra_validators_repl = ["extra.py"]

    def _leer_linea_factory():
        entradas = iter(["imprimir(1)", "salir"])
        return lambda _prompt: next(entradas)

    with patch.object(cmd, "validar_entrada", return_value=True), \
         patch.object(cmd, "_ejecutar_en_sandbox") as mock_sandbox:
        cmd._run_repl_loop(
            args=_args(),
            validador=None,
            leer_linea=_leer_linea_factory(),
            sandbox=True,
            sandbox_docker=None,
        )

    mock_sandbox.assert_called_once_with(
        "imprimir(1)",
    )


def test_ejecutar_en_sandbox_usa_estado_repl_y_contrato_de_run_service():
    cmd = InteractiveCommand(MagicMock())
    cmd._seguro_repl = True
    cmd._extra_validators_repl = ["extra_repl.py"]
    with patch.dict(
        cmd._ejecutar_en_sandbox.__globals__,
        {
            "prevalidar_y_parsear_codigo": MagicMock(),
            "construir_script_sandbox_canonico": MagicMock(return_value="SCRIPT"),
            "ejecutar_en_sandbox": MagicMock(return_value=None),
        },
    ) as patched_globals:
        mock_prevalidar = patched_globals["prevalidar_y_parsear_codigo"]
        mock_script = patched_globals["construir_script_sandbox_canonico"]
        mock_ejecutar = patched_globals["ejecutar_en_sandbox"]
        cmd._ejecutar_en_sandbox("imprimir(7)")
    mock_prevalidar.assert_called_once_with("imprimir(7)")
    mock_script.assert_called_once_with(
        "imprimir(7)",
        safe_mode=True,
        extra_validators=["extra_repl.py"],
        imprimir_resultado=True,
    )
    mock_ejecutar.assert_called_once_with(
        "SCRIPT",
        allow_insecure_fallback=False,
    )


def test_format_user_error_limpia_prefijo_error_general():
    mensaje = format_user_error(RuntimeError("Error general: La condición debe ser booleana"))
    assert mensaje == "La condición debe ser booleana"


def test_format_user_error_elimina_prefijos_redundantes_en_bucle():
    mensaje = format_user_error(RuntimeError("Error: Error general: La condición debe ser booleana"))
    assert mensaje == "La condición debe ser booleana"


def test_format_user_error_normaliza_prefijos_redundantes_adicionales():
    assert (
        format_user_error(RuntimeError("Error general: La condición debe ser booleana"))
        == "La condición debe ser booleana"
    )
    assert (
        format_user_error(RuntimeError("Error: Error general: La condición debe ser booleana"))
        == "La condición debe ser booleana"
    )
    assert format_user_error(RuntimeError("Error crítico - Error: mensaje")) == "mensaje"


def test_log_error_imprime_mensaje_limpio_sin_categoria_tecnica():
    cmd = InteractiveCommand(MagicMock())

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        cmd._log_error("Error de sintaxis", RuntimeError("Error: Error general: fallo"))

    assert mock_stdout.getvalue().strip() == "Error: fallo"


def test_run_repl_loop_reporta_error_sandbox_una_sola_vez():
    cmd = InteractiveCommand(MagicMock())

    def _leer_linea_factory():
        entradas = iter(["imprimir(1)", "salir"])
        return lambda _prompt: next(entradas)

    with patch.object(cmd, "validar_entrada", return_value=True), \
         patch.object(cmd, "_ejecutar_en_sandbox", side_effect=RuntimeError("Error general: fallo controlado")), \
         patch("cobra.cli.commands.interactive_cmd.mostrar_error") as mock_error:
        cmd._run_repl_loop(
            args=_args(),
            validador=None,
            leer_linea=_leer_linea_factory(),
            sandbox=True,
            sandbox_docker=None,
        )

    mock_error.assert_called_once_with("fallo controlado", registrar_log=False)


def test_es_error_de_bloque_incompleto_usa_fallback_textual_si_falta_metadata():
    cmd = InteractiveCommand(MagicMock())
    err = ParserError("Unexpected EOF: se esperaba 'fin' para cerrar el bloque")
    assert cmd._es_error_de_bloque_incompleto(err) is True


def test_es_error_de_bloque_incompleto_no_aplica_fallback_a_lexer_ni_runtime():
    cmd = InteractiveCommand(MagicMock())
    assert cmd._es_error_de_bloque_incompleto(
        LexerError("Unexpected EOF: se esperaba 'fin'", 1, 1)
    ) is False
    assert cmd._es_error_de_bloque_incompleto(RuntimeError("Unexpected EOF: se esperaba 'fin'")) is False


def test_run_repl_loop_continue_mantiene_buffer_en_error_incompleto_por_fallback():
    cmd = InteractiveCommand(MagicMock())
    entradas = iter(["si verdadero:", "imprimir(1)", "fin", "salir"])
    parse_calls: list[str] = []
    ejecutados: list[str] = []

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo != "si verdadero:\nimprimir(1)\nfin":
            raise ParserError("Unexpected EOF: se esperaba 'fin' para cerrar el bloque")
        return []

    with patch.object(cmd, "validar_entrada", return_value=True), \
         patch("cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo", side_effect=_fake_parse), \
         patch.object(cmd, "ejecutar_codigo", side_effect=lambda codigo, _validador: ejecutados.append(codigo)):
        cmd._run_repl_loop(
            args=_args(),
            validador=None,
            leer_linea=lambda _prompt: next(entradas),
            sandbox=False,
            sandbox_docker=None,
        )

    assert parse_calls == [
        "si verdadero:",
        "si verdadero:\nimprimir(1)",
        "si verdadero:\nimprimir(1)\nfin",
    ]
    assert ejecutados == ["si verdadero:\nimprimir(1)\nfin"]


def test_run_repl_loop_bloque_si_parsea_buffer_completo_y_ejecuta_al_cerrar():
    cmd = InteractiveCommand(MagicMock())
    entradas = iter(["si x > 5:", "imprimir(x)", "fin", "salir"])
    prompts: list[str] = []
    parse_calls: list[str] = []
    ejecutados: list[str] = []

    def _leer_linea(prompt: str) -> str:
        prompts.append(prompt)
        return next(entradas)

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo != "si x > 5:\nimprimir(x)\nfin":
            raise ParserError("Unexpected EOF: se esperaba 'fin' para cerrar el bloque")
        return []

    with patch.object(cmd, "validar_entrada", return_value=True), \
         patch("cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo", side_effect=_fake_parse), \
         patch.object(cmd, "ejecutar_codigo", side_effect=lambda codigo, _validador: ejecutados.append(codigo)), \
         patch.object(cmd, "_log_error") as mock_log_error:
        cmd._run_repl_loop(
            args=_args(),
            validador=None,
            leer_linea=_leer_linea,
            sandbox=False,
            sandbox_docker=None,
        )

    assert prompts[:4] == [">>> ", "... ", "... ", ">>> "]
    assert parse_calls == [
        "si x > 5:",
        "si x > 5:\nimprimir(x)",
        "si x > 5:\nimprimir(x)\nfin",
    ]
    assert ejecutados == ["si x > 5:\nimprimir(x)\nfin"]
    mock_log_error.assert_not_called()
    assert cmd._estado_repl["buffer_lineas"] == []


def test_run_repl_loop_error_sintactico_real_limpia_buffer_y_permite_recuperacion():
    cmd = InteractiveCommand(MagicMock())
    entradas = iter(["si x > 5:", "imprimir(x", "imprimir(99)", "salir"])
    parse_calls: list[str] = []
    ejecutados: list[str] = []

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)
        if codigo == "si x > 5:\nimprimir(x":
            raise ParserError("Error de sintaxis: falta ')' en llamada a imprimir")
        if codigo == "si x > 5:":
            raise ParserError("Unexpected EOF: se esperaba 'fin' para cerrar el bloque")
        return []

    with patch.object(cmd, "validar_entrada", return_value=True), \
         patch("cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo", side_effect=_fake_parse), \
         patch.object(cmd, "ejecutar_codigo", side_effect=lambda codigo, _validador: ejecutados.append(codigo)), \
         patch.object(cmd, "_log_error") as mock_log_error:
        cmd._run_repl_loop(
            args=_args(),
            validador=None,
            leer_linea=lambda _prompt: next(entradas),
            sandbox=False,
            sandbox_docker=None,
        )

    assert parse_calls == [
        "si x > 5:",
        "si x > 5:\nimprimir(x",
        "imprimir(99)",
    ]
    mock_log_error.assert_called_once()
    categoria_error, err = mock_log_error.call_args.args
    assert categoria_error == "Error de sintaxis"
    assert "falta ')'" in str(err)
    assert ejecutados == ["imprimir(99)"]
    assert cmd._estado_repl["buffer_lineas"] == []
