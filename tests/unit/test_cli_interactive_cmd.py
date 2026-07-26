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
    fake_path = tmp_path / ".cobra_history"
    fake_history = object()

    cmd = InteractiveCommand(MagicMock())
    run_globals = InteractiveCommand.run.__globals__
    os_module = run_globals["os"]

    mock_expanduser = MagicMock(return_value=str(fake_path))
    mock_makedirs = MagicMock()
    mock_prompt_session = MagicMock()
    mock_prompt_session.return_value.prompt.side_effect = ["salir"]
    mock_validar_dependencias = MagicMock()

    with patch.object(
        os_module.path,
        "expanduser",
        mock_expanduser,
    ), patch.object(
        os_module,
        "makedirs",
        mock_makedirs,
    ), patch.object(
        cmd,
        "_construir_historial",
        return_value=fake_history,
    ) as mock_construir_historial, patch.dict(
        run_globals,
        {
            "PromptSession": mock_prompt_session,
            "validar_dependencias": mock_validar_dependencias,
        },
        clear=False,
    ):
        resultado = cmd.run(_args())

    assert resultado == 0
    mock_expanduser.assert_called_once_with("~/.cobra_history")
    mock_makedirs.assert_called_once_with(
        str(tmp_path),
        exist_ok=True,
    )
    mock_construir_historial.assert_called_once_with(str(fake_path))

    assert mock_prompt_session.call_count == 1
    assert mock_prompt_session.call_args.kwargs["history"] is fake_history

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
    mock_ejecutar.assert_called_once()
    args_llamada, kwargs_llamada = mock_ejecutar.call_args
    assert args_llamada == ('si verdadero:\nvar x = 1\nimprimir(x)\nfin', None)
    assert "ast_preparseado" in kwargs_llamada
    assert len(kwargs_llamada["ast_preparseado"]) == 1

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
    mock_ejecutar.assert_called_once()
    args_llamada, kwargs_llamada = mock_ejecutar.call_args
    assert args_llamada == ('si verdadero:\ntokens\nimprimir "ok"\nfin', None)
    assert "ast_preparseado" in kwargs_llamada
    assert len(kwargs_llamada["ast_preparseado"]) == 1
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
    interp.ejecutar_nodo.return_value = True

    cmd = InteractiveCommand(interp)
    cmd._seguro_repl = False

    nodo = object()

    with patch(
        "sys.stdout",
        new_callable=StringIO,
    ) as mock_stdout:
        cmd.ejecutar_codigo(
            "codigo",
            validador=None,
            ast_preparseado=[nodo],
        )

    assert mock_stdout.getvalue().strip() == "verdadero"
    interp.ejecutar_nodo.assert_called_once_with(nodo)

def test_ejecutar_codigo_imprime_booleano_falso():
    interp = MagicMock()
    interp.ejecutar_nodo.return_value = False

    cmd = InteractiveCommand(interp)
    cmd._seguro_repl = False

    nodo = object()

    with patch(
        "sys.stdout",
        new_callable=StringIO,
    ) as mock_stdout:
        cmd.ejecutar_codigo(
            "codigo",
            validador=None,
            ast_preparseado=[nodo],
        )

    assert mock_stdout.getvalue().strip() == "falso"
    interp.ejecutar_nodo.assert_called_once_with(nodo)

def test_ejecutar_codigo_imprime_valor_sin_transformacion():
    interp = MagicMock()
    interp.ejecutar_nodo.return_value = "resultado"

    cmd = InteractiveCommand(interp)
    cmd._seguro_repl = False

    nodo = object()

    with patch(
        "sys.stdout",
        new_callable=StringIO,
    ) as mock_stdout:
        cmd.ejecutar_codigo(
            "codigo",
            validador=None,
            ast_preparseado=[nodo],
        )

    assert mock_stdout.getvalue().strip() == "resultado"
    interp.ejecutar_nodo.assert_called_once_with(nodo)

def test_ejecutar_codigo_no_imprime_cuando_resultado_es_none():
    interp = MagicMock()
    interp.ejecutar_nodo.return_value = None

    cmd = InteractiveCommand(interp)
    cmd._seguro_repl = False

    nodo = object()

    with patch(
        "sys.stdout",
        new_callable=StringIO,
    ) as mock_stdout:
        cmd.ejecutar_codigo(
            "codigo",
            validador=None,
            ast_preparseado=[nodo],
        )

    assert mock_stdout.getvalue() == ""
    interp.ejecutar_nodo.assert_called_once_with(nodo)

def test_ejecutar_codigo_intenta_fallback_para_expresion_top_level_no_soportada():
    cmd = InteractiveCommand(MagicMock())

    ast_original = [object()]
    ast_fallback = [object()]
    error_original = ValueError(
        "Nodo no soportado: "
        "<class 'pcobra.core.ast_nodes.NodoOperacionBinaria'>"
    )
    codigos_prevalidados = []

    def _prevalidar(codigo):
        codigos_prevalidados.append(codigo)
        if codigo == "1 + 2":
            return ast_original
        if codigo == "imprimir(1 + 2)":
            return ast_fallback
        raise AssertionError(f"Código inesperado: {codigo}")

    globals_run = InteractiveCommand.ejecutar_codigo.__globals__

    with patch.dict(
        globals_run,
        {"prevalidar_y_parsear_codigo": _prevalidar},
        clear=False,
    ), patch.object(
        cmd,
        "_validar_ast_para_analisis",
    ), patch.object(
        cmd,
        "_ejecutar_ast_en_repl",
        side_effect=[
            error_original,
            (ast_fallback, None),
        ],
    ) as mock_ejecutar_ast, patch.object(
        cmd,
        "_debe_intentar_fallback_expresion_top_level",
        return_value=True,
    ) as mock_debe_fallback, patch.object(
        cmd,
        "_imprimir_resultado_repl",
    ) as mock_imprimir:
        cmd.ejecutar_codigo("1 + 2")

    assert codigos_prevalidados == [
        "1 + 2",
        "imprimir(1 + 2)",
    ]
    assert mock_ejecutar_ast.call_count == 2
    assert mock_ejecutar_ast.call_args_list[0].args[0] is ast_original
    assert mock_ejecutar_ast.call_args_list[1].args[0] is ast_fallback

    mock_debe_fallback.assert_called_once_with(
        "1 + 2",
        error_original,
    )
    mock_imprimir.assert_called_once_with(ast_fallback, None)

def test_ejecutar_codigo_prioriza_error_original_cuando_fallback_tambien_falla():
    cmd = InteractiveCommand(MagicMock())

    ast_original = [object()]
    ast_fallback = [object()]
    error_original = ValueError(
        "Nodo no soportado: "
        "<class 'pcobra.core.ast_nodes.NodoOperacionBinaria'>"
    )
    error_fallback = RuntimeError(
        "Nodo no soportado durante fallback"
    )
    codigos_prevalidados = []

    def _prevalidar(codigo):
        codigos_prevalidados.append(codigo)
        if codigo == "1 + 2":
            return ast_original
        if codigo == "imprimir(1 + 2)":
            return ast_fallback
        raise AssertionError(f"Código inesperado: {codigo}")

    globals_run = InteractiveCommand.ejecutar_codigo.__globals__

    with patch.dict(
        globals_run,
        {"prevalidar_y_parsear_codigo": _prevalidar},
        clear=False,
    ), patch.object(
        cmd,
        "_validar_ast_para_analisis",
    ), patch.object(
        cmd,
        "_ejecutar_ast_en_repl",
        side_effect=[
            error_original,
            error_fallback,
        ],
    ) as mock_ejecutar_ast, patch.object(
        cmd,
        "_debe_intentar_fallback_expresion_top_level",
        return_value=True,
    ) as mock_debe_fallback:
        try:
            cmd.ejecutar_codigo("1 + 2")
            assert False, "Se esperaba excepción"
        except ValueError as err:
            assert err is error_original
            assert str(err) == str(error_original)
            assert str(error_fallback) not in str(err)

    assert codigos_prevalidados == [
        "1 + 2",
        "imprimir(1 + 2)",
    ]
    assert mock_ejecutar_ast.call_count == 2
    assert mock_debe_fallback.call_count == 2

def test_ejecutar_codigo_no_intenta_fallback_si_no_es_expresion_top_level():
    cmd = InteractiveCommand(MagicMock())

    NodoAsignacion = type("NodoAsignacion", (), {})
    ast_stmt = [NodoAsignacion()]
    error_original = ValueError(
        "Nodo no soportado: "
        "<class 'pcobra.core.ast_nodes.NodoAsignacion'>"
    )
    codigos_prevalidados = []

    def _prevalidar(codigo):
        codigos_prevalidados.append(codigo)
        return ast_stmt

    globals_run = InteractiveCommand.ejecutar_codigo.__globals__

    with patch.dict(
        globals_run,
        {"prevalidar_y_parsear_codigo": _prevalidar},
        clear=False,
    ), patch.object(
        cmd,
        "_validar_ast_para_analisis",
    ), patch.object(
        cmd,
        "_ejecutar_ast_en_repl",
        side_effect=error_original,
    ) as mock_ejecutar_ast:
        try:
            cmd.ejecutar_codigo("var x = 1")
            assert False, "Se esperaba excepción"
        except ValueError as err:
            assert err is error_original
            assert "Nodo no soportado" in str(err)

    # Primera llamada: análisis normal.
    # Segunda llamada: clasificación real del posible fallback.
    assert codigos_prevalidados == [
        "var x = 1",
        "var x = 1",
    ]
    assert "imprimir(var x = 1)" not in codigos_prevalidados
    assert mock_ejecutar_ast.call_count == 1

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

        def ejecutar_nodo(self, nodo):
            self.ultimo_resultado = True
            return self.ultimo_resultado

    interp = _InterpretadorDummy()
    cmd = InteractiveCommand(interp)
    cmd._seguro_repl = False

    nodo = object()

    with patch(
        "sys.stdout",
        new_callable=StringIO,
    ) as mock_stdout:
        cmd.ejecutar_codigo(
            "codigo",
            validador=None,
            ast_preparseado=[nodo],
        )

    assert mock_stdout.getvalue().strip() == "verdadero"
    assert interp.ultimo_resultado is True
    assert isinstance(interp.ultimo_resultado, bool)

def test_ejecutar_ast_en_repl_ejecuta_nodo_a_nodo_y_no_batch_ejecutar_ast():
    interp = MagicMock()
    interp.ejecutar_nodo.side_effect = ["primer resultado", "resultado final"]

    cmd = InteractiveCommand(interp)
    cmd._seguro_repl = False

    nodo_1 = object()
    nodo_2 = object()
    ast_original = [nodo_1, nodo_2]

    ast, resultado = cmd._ejecutar_ast_en_repl(ast_original)

    assert ast is ast_original
    assert resultado == "resultado final"
    assert [
        llamada.args
        for llamada in interp.ejecutar_nodo.call_args_list
    ] == [
        (nodo_1,),
        (nodo_2,),
    ]
    interp.ejecutar_ast.assert_not_called()

def test_parsear_y_ejecutar_codigo_repl_restaurar_interpretador_de_sesion():
    cmd = InteractiveCommand(MagicMock(name="interp_sesion"))
    cmd._interpretador_sesion = cmd.interpretador
    cmd.interpretador = MagicMock(name="interp_temporal")

    with patch('cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo'), \
         patch.object(cmd, 'ejecutar_codigo') as mock_ejecutar:
        cmd.parsear_y_ejecutar_codigo_repl("imprimir(1)")

    assert cmd.interpretador is cmd._interpretador_sesion
    mock_ejecutar.assert_called_once()

    args, kwargs = mock_ejecutar.call_args

    assert args == ("imprimir(1)", None)
    assert "ast_preparseado" in kwargs
    assert kwargs["ast_preparseado"] is not None
    assert len(kwargs["ast_preparseado"]) == 1


def test_parsear_y_ejecutar_codigo_repl_no_invoca_pipeline_explicito_en_ruta_normal():
    cmd = InteractiveCommand(MagicMock())

    ast_preparseado = [object()]
    mock_prevalidar = MagicMock(return_value=ast_preparseado)

    with patch.object(
        cmd,
        "ejecutar_codigo",
    ) as mock_ejecutar:
        cmd.parsear_y_ejecutar_codigo_repl(
            "imprimir(1)",
            prevalidar_fn=mock_prevalidar,
        )

    mock_prevalidar.assert_called_once_with("imprimir(1)")
    mock_ejecutar.assert_called_once_with(
        "imprimir(1)",
        None,
        ast_preparseado=ast_preparseado,
    )

def test_ejecutar_en_sandbox_arma_script_con_captura_y_booleanos():
    cmd = InteractiveCommand(MagicMock())
    cmd._seguro_repl = False
    cmd._extra_validators_repl = ["validador.py"]
    cmd._allow_insecure_fallback = False

    interpretador_cls = type("InterpretadorSandboxDummy", (), {})
    setup = SimpleNamespace(
        interpretador=cmd.interpretador,
        safe_mode=False,
        validadores_extra=["validador.py"],
    )

    with patch(
        "cobra.cli.commands.interactive_cmd.resolver_interpretador_cls",
        return_value=interpretador_cls,
    ) as mock_resolver, patch.object(
        cmd,
        "_ejecutar_pipeline_explicito_solo_setup_sandbox",
        return_value=setup,
    ) as mock_setup, patch.object(
        cmd,
        "_sincronizar_interpretador_sesion",
    ) as mock_sincronizar, patch.object(
        cmd,
        "_configurar_restriccion_usar_repl",
    ) as mock_configurar_usar, patch(
        "cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo",
        return_value=[],
    ) as mock_prevalidar, patch(
        "cobra.cli.commands.interactive_cmd.ejecutar_en_sandbox",
        return_value="ok",
    ) as mock_sandbox, patch(
        "cobra.cli.commands.interactive_cmd.mostrar_info",
    ) as mock_info:
        cmd._ejecutar_en_sandbox("imprimir(1)")

    mock_resolver.assert_called_once()
    mock_setup.assert_called_once_with(interpretador_cls)
    mock_sincronizar.assert_called_once_with()
    mock_configurar_usar.assert_called_once_with()
    mock_prevalidar.assert_called_once_with("imprimir(1)")

    script_enviado = mock_sandbox.call_args.args[0]

    assert "safe_mode=False" in script_enviado
    assert "extra_validators=['validador.py']" in script_enviado
    assert "cobra_resultado = cobra_interp.ejecutar_ast(cobra_ast)" in script_enviado
    assert "if cobra_resultado is not None:" in script_enviado
    assert "if isinstance(cobra_resultado, bool):" in script_enviado
    assert "print('verdadero' if cobra_resultado else 'falso')" in script_enviado
    assert "print(cobra_resultado)" in script_enviado

    mock_sandbox.assert_called_once_with(
        script_enviado,
        allow_insecure_fallback=False,
    )
    mock_info.assert_called_once_with("ok")

    assert cmd._seguro_repl is False
    assert cmd._extra_validators_repl == ["validador.py"]

def test_ejecutar_en_sandbox_invoca_pipeline_explicito_solo_para_setup():
    cmd = InteractiveCommand(MagicMock(name="interp_original"))
    interp_original = cmd.interpretador
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
    assert cmd.interpretador is interp_original
    assert cmd.interpretador is not setup.interpretador
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
    interp_original = MagicMock(name="interp_original")
    cmd = InteractiveCommand(interp_original)

    cmd._seguro_repl = False
    cmd._extra_validators_repl = ["extra_repl.py"]
    cmd._allow_insecure_fallback = True

    interpretador_cls = type("InterpretadorSandboxDummy", (), {})

    setup = SimpleNamespace(
        interpretador=MagicMock(name="interp_setup"),
        safe_mode=False,
        validadores_extra=["extra_repl.py"],
    )

    mock_resolver = MagicMock(return_value=interpretador_cls)
    mock_prevalidar = MagicMock(return_value=[])
    mock_construir_script = MagicMock(return_value="SCRIPT")
    mock_ejecutar = MagicMock(return_value=None)
    mock_mostrar_info = MagicMock()

    globals_sandbox = InteractiveCommand._ejecutar_en_sandbox.__globals__

    with patch.dict(
        globals_sandbox,
        {
            "resolver_interpretador_cls": mock_resolver,
            "prevalidar_y_parsear_codigo": mock_prevalidar,
            "construir_script_sandbox_canonico": mock_construir_script,
            "ejecutar_en_sandbox": mock_ejecutar,
            "mostrar_info": mock_mostrar_info,
        },
        clear=False,
    ), patch.object(
        cmd,
        "_ejecutar_pipeline_explicito_solo_setup_sandbox",
        return_value=setup,
    ) as mock_setup, patch.object(
        cmd,
        "_sincronizar_interpretador_sesion",
    ) as mock_sincronizar, patch.object(
        cmd,
        "_configurar_restriccion_usar_repl",
    ) as mock_configurar_usar:
        cmd._ejecutar_en_sandbox("imprimir(7)")

    mock_resolver.assert_called_once()
    mock_setup.assert_called_once_with(interpretador_cls)

    mock_sincronizar.assert_called_once_with()
    mock_configurar_usar.assert_called_once_with()
    mock_prevalidar.assert_called_once_with("imprimir(7)")

    mock_construir_script.assert_called_once_with(
        "imprimir(7)",
        safe_mode=False,
        extra_validators=["extra_repl.py"],
        imprimir_resultado=True,
    )

    mock_ejecutar.assert_called_once_with(
        "SCRIPT",
        allow_insecure_fallback=True,
    )

    mock_mostrar_info.assert_not_called()

    # El setup normaliza políticas, pero no reemplaza el intérprete
    # incremental activo de la sesión.
    assert cmd.interpretador is interp_original
    assert cmd.interpretador is not setup.interpretador
    assert cmd._seguro_repl is False
    assert cmd._extra_validators_repl == ["extra_repl.py"]

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


def test_run_repl_loop_acumula_buffer_hasta_fin_y_parsea_una_sola_vez():
    cmd = InteractiveCommand(MagicMock())

    entradas = iter([
        "si verdadero:",
        "imprimir(1)",
        "fin",
        "salir",
    ])

    codigo_final = "\n".join([
        "si verdadero:",
        "imprimir(1)",
        "fin",
    ])
    ast_final = [object()]
    parse_calls = []

    def fake_parse(codigo: str):
        parse_calls.append(codigo)
        assert codigo == codigo_final
        return ast_final

    with patch.object(
        cmd,
        "validar_entrada",
        return_value=True,
    ), patch(
        "cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo",
        side_effect=fake_parse,
    ), patch.object(
        cmd,
        "ejecutar_codigo",
    ) as mock_ejecutar:
        cmd._run_repl_loop(
            args=SimpleNamespace(),
            validador=None,
            leer_linea=lambda _prompt: next(entradas),
            sandbox=False,
            sandbox_docker=None,
        )

    assert parse_calls == [codigo_final]
    mock_ejecutar.assert_called_once_with(
        codigo_final,
        None,
        ast_preparseado=ast_final,
    )

def test_run_repl_loop_bloque_si_parsea_buffer_completo_y_ejecuta_al_cerrar():
    cmd = InteractiveCommand(MagicMock())

    entradas = iter([
        "si x > 5:",
        "imprimir(x)",
        "fin",
        "salir",
    ])

    codigo_final = "\n".join([
        "si x > 5:",
        "imprimir(x)",
        "fin",
    ])
    ast_final = [object()]
    parse_calls = []

    def fake_parse(codigo: str):
        parse_calls.append(codigo)
        assert codigo == codigo_final
        return ast_final

    with patch.object(
        cmd,
        "validar_entrada",
        return_value=True,
    ), patch(
        "cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo",
        side_effect=fake_parse,
    ), patch.object(
        cmd,
        "ejecutar_codigo",
    ) as mock_ejecutar:
        cmd._run_repl_loop(
            args=SimpleNamespace(),
            validador=None,
            leer_linea=lambda _prompt: next(entradas),
            sandbox=False,
            sandbox_docker=None,
        )

    assert parse_calls == [codigo_final]
    mock_ejecutar.assert_called_once_with(
        codigo_final,
        None,
        ast_preparseado=ast_final,
    )

def test_run_repl_loop_error_sintactico_real_limpia_buffer_y_permite_recuperacion():
    cmd = InteractiveCommand(MagicMock())

    entradas = iter([
        "si x > 5:",
        "imprimir(x",
        "fin",
        "imprimir(99)",
        "salir",
    ])

    codigo_erroneo = "\n".join([
        "si x > 5:",
        "imprimir(x",
        "fin",
    ])
    codigo_recuperacion = "imprimir(99)"
    ast_recuperacion = []

    parse_calls: list[str] = []
    ejecutados = []

    def _fake_parse(codigo: str):
        parse_calls.append(codigo)

        if codigo == codigo_erroneo:
            raise ParserError(
                "Error de sintaxis: falta ')' en llamada a imprimir"
            )

        if codigo == codigo_recuperacion:
            return ast_recuperacion

        raise AssertionError(f"Código inesperado: {codigo!r}")

    def _registrar_ejecucion(
        codigo,
        _validador=None,
        *,
        ast_preparseado=None,
    ):
        ejecutados.append((codigo, ast_preparseado))

    with patch.object(
        cmd,
        "validar_entrada",
        return_value=True,
    ), patch(
        "cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo",
        side_effect=_fake_parse,
    ), patch.object(
        cmd,
        "ejecutar_codigo",
        side_effect=_registrar_ejecucion,
    ), patch.object(
        cmd,
        "_log_error",
    ) as mock_log_error:
        cmd._run_repl_loop(
            args=SimpleNamespace(),
            validador=None,
            leer_linea=lambda _prompt: next(entradas),
            sandbox=False,
            sandbox_docker=None,
        )

    assert parse_calls == [
        codigo_erroneo,
        codigo_recuperacion,
    ]

    mock_log_error.assert_called_once()
    categoria_error, err = mock_log_error.call_args.args
    assert categoria_error == "Error de sintaxis"
    assert "falta ')'" in str(err)

    assert ejecutados == [
        (codigo_recuperacion, ast_recuperacion),
    ]
    assert cmd._estado_repl["buffer_lineas"] == []
    assert cmd._estado_repl["nivel_bloque"] == 0

def test_ejecutar_codigo_restaurar_modo_previo_tras_ejecucion_repl():
    class _NodoDummy:
        def aceptar(self, _validador):
            return None

    class _InterpDummy:
        def __init__(self):
            self.mode = "analysis"

        def ejecutar_nodo(self, _nodo):
            return 7

    interp = _InterpDummy()
    cmd = InteractiveCommand(interp)
    ast_dummy = [_NodoDummy()]

    with patch(
        "cobra.cli.commands.interactive_cmd.prevalidar_y_parsear_codigo",
        return_value=ast_dummy,
    ), patch.object(cmd, "_imprimir_resultado_repl"):
        cmd.ejecutar_codigo("1 + 6")

    assert cmd.mode == "analysis"
    assert interp.mode == "analysis"
