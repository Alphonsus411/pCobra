"""Pruebas focales de POO-004: instanciación alcanzable desde fuente."""

import logging
from argparse import Namespace
from types import SimpleNamespace

import pcobra.jupyter_kernel as jupyter_kernel
from pcobra.cobra.cli.commands import (
    bench_transpilers_cmd,
    benchthreads_cmd,
    compile_cmd,
    profile_cmd,
)
from pcobra.cobra.cli.commands.bench_transpilers_cmd import BenchTranspilersCommand
from pcobra.cobra.cli.commands.compile_cmd import CompileCommand
from pcobra.cobra.cli.services import test_service, verification_service
from pcobra.cobra.cli.services.contracts import TestRequest as CobraTestRequest
from pcobra.cobra.core.ast_nodes import (
    NodoAsignacion,
    NodoClase,
    NodoIdentificador,
    NodoInstancia,
    NodoLlamadaFuncion,
    NodoLlamadaMetodo,
    NodoValor,
)
from pcobra.cobra.core.lexer import Lexer
from pcobra.cobra.core.parser import Parser
from pcobra.cobra.core.resolucion_instancias import resolver_instanciaciones
from pcobra.cobra.core.parsing import parsear_codigo_resuelto
from pcobra.core.import_utils import cargar_ast_modulo


def _parsear(codigo: str):
    ast_sintactico = Parser(Lexer(codigo).analizar_token()).parsear()
    return resolver_instanciaciones(ast_sintactico)


def _valor_asignado(nodo):
    assert type(nodo) is NodoAsignacion
    return nodo.expresion


def test_parser_puro_conserva_llamada_sintactica():
    ast = Parser(
        Lexer("clase Persona:\nfin\nvar persona = Persona()").analizar_token()
    ).parsear()

    assert type(_valor_asignado(ast[1])) is NodoLlamadaFuncion


def test_frontera_publica_sin_sqlite_devuelve_instancia(monkeypatch):
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)

    ast = parsear_codigo_resuelto(
        "clase Persona:\nfin\nvar persona = Persona()"
    )

    assert type(_valor_asignado(ast[1])) is NodoInstancia


def test_jupyter_entrega_ast_resuelto_al_interprete(monkeypatch):
    capturado = {}

    class Interprete:
        def ejecutar_ast(self, ast):
            capturado["ast"] = ast

    kernel = SimpleNamespace(
        _lexer_cls=Lexer,
        _parser_cls=Parser,
        _get_suggestions=lambda: [],
        interpreter=Interprete(),
        use_python=False,
        execution_count=1,
    )
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)

    resultado = jupyter_kernel.CobraKernel.do_execute(
        kernel,
        "clase Persona:\nfin\nvar persona = Persona()",
        silent=True,
    )

    assert resultado["status"] == "ok"
    assert type(_valor_asignado(capturado["ast"][1])) is NodoInstancia


def test_profile_entrega_ast_resuelto_al_interprete(
    tmp_path, monkeypatch, capsys
):
    capturado = {}
    archivo = tmp_path / "persona.cobra"
    archivo.write_text(
        "clase Persona:\nfin\nvar persona = Persona()", encoding="utf-8"
    )

    class Interprete:
        def ejecutar_ast(self, ast):
            capturado["ast"] = ast

    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.setattr(profile_cmd, "validar_dependencias", lambda *_args: None)
    monkeypatch.setattr(
        profile_cmd,
        "construir_interprete_seguro_canonico",
        lambda **_kwargs: Interprete(),
    )

    resultado = profile_cmd.ProfileCommand().run(
        Namespace(
            archivo=str(archivo),
            output=None,
            ui=None,
            depurar=False,
            formatear=False,
            seguro=False,
            extra_validators=None,
            analysis=True,
        )
    )

    assert resultado == 0
    assert type(_valor_asignado(capturado["ast"][1])) is NodoInstancia
    salida = capsys.readouterr().out
    assert "Parser profile" in salida


def test_benchthreads_entrega_ast_resuelto_al_interprete(tmp_path, monkeypatch):
    capturado = {}
    archivo = tmp_path / "sequential.cobra"
    archivo.write_text(
        "clase Persona:\nfin\nvar persona = Persona()", encoding="utf-8"
    )

    class Interprete:
        def ejecutar_ast(self, ast):
            capturado["ast"] = ast

    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.setattr(benchthreads_cmd, "SEQUENTIAL_CODE", archivo)
    monkeypatch.setattr(
        benchthreads_cmd,
        "construir_interprete_seguro_canonico",
        lambda **_kwargs: Interprete(),
    )

    benchthreads_cmd.BenchThreadsCommand()._run_sequential()

    assert type(_valor_asignado(capturado["ast"][1])) is NodoInstancia


def test_test_service_entrega_ast_resuelto_a_runtime_y_transpilacion(monkeypatch):
    capturados = []
    codigo = "clase Persona:\nfin\nvar persona = Persona()"

    class Interprete:
        def ejecutar_ast(self, ast):
            capturados.append(ast)

    servicio = test_service.TestService.__new__(test_service.TestService)
    servicio._interprete = Interprete()
    servicio._logger = logging.getLogger(__name__)
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.setattr(servicio, "read_source_file", lambda _archivo: codigo)
    monkeypatch.setattr(
        servicio,
        "verify_language",
        lambda _lang, ast, _esperado: (capturados.append(ast) or ("python", None)),
    )

    resultado = servicio.run(CobraTestRequest("persona.cobra", ["python"]))

    assert resultado == 0
    assert len(capturados) == 2
    assert all(type(_valor_asignado(ast[1])) is NodoInstancia for ast in capturados)


def test_verification_service_entrega_ast_resuelto_a_runtime_y_transpilacion(
    tmp_path, monkeypatch
):
    capturados = []
    archivo = tmp_path / "persona.cobra"
    archivo.write_text(
        "clase Persona:\nfin\nvar persona = Persona()", encoding="utf-8"
    )

    class Interprete:
        def ejecutar_ast(self, ast):
            capturados.append(ast)

    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.setattr(
        verification_service,
        "construir_interprete_seguro_canonico",
        lambda **_kwargs: Interprete(),
    )
    monkeypatch.setattr(
        verification_service,
        "_compile_and_execute",
        lambda ast, _lang: (capturados.append(ast) or ("", None)),
    )

    resultado = verification_service.execute_runtime_verification(
        str(archivo), ["python"]
    )

    assert resultado == 0
    assert len(capturados) == 2
    assert all(type(_valor_asignado(ast[1])) is NodoInstancia for ast in capturados)


def test_compile_sin_sqlite_alcanza_transpilacion_con_ast_resuelto(
    tmp_path, monkeypatch
):
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    archivo = tmp_path / "persona.cobra"
    archivo.write_text(
        "clase Persona:\nfin\nvar persona = Persona()", encoding="utf-8"
    )
    capturado = {}

    monkeypatch.setattr(compile_cmd, "validar_politica_modo", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(compile_cmd, "cli_transpilers", lambda: {"python": object})
    monkeypatch.setattr(compile_cmd, "cli_plugin_transpilers", lambda: {})
    monkeypatch.setattr(compile_cmd, "cli_toml_map", lambda: {})
    monkeypatch.setattr(
        compile_cmd, "validar_dependencias_con_alias", lambda *_args: None
    )
    monkeypatch.setattr(
        compile_cmd.backend_pipeline,
        "resolve_backend_runtime",
        lambda *_args, **_kwargs: (SimpleNamespace(backend="python"), {}),
    )
    monkeypatch.setattr(
        compile_cmd,
        "_transpile_with_pipeline_or_plugin",
        lambda ast, *_args, **_kwargs: capturado.setdefault("ast", ast) or "ok",
    )

    assert CompileCommand.requires_sqlite_key is False
    resultado = CompileCommand().run(
        SimpleNamespace(
            archivo=str(archivo),
            tipo="python",
            backend=None,
            tipos=None,
            modo="mixto",
        )
    )

    assert resultado == 0
    assert type(_valor_asignado(capturado["ast"][1])) is NodoInstancia


def test_benchtranspilers_sin_sqlite_alcanza_transpilacion_con_ast_resuelto(
    tmp_path, monkeypatch
):
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    codigo = "clase Persona:\nfin\nvar persona = Persona()"
    capturados = []
    for size in bench_transpilers_cmd.VALID_SIZES:
        (tmp_path / f"{size}.cobra").write_text(codigo, encoding="utf-8")

    class Transpilador:
        def generate_code(self, ast):
            capturados.append(ast)
            return "ok"

    monkeypatch.setattr(bench_transpilers_cmd, "PROGRAM_DIR", tmp_path)
    monkeypatch.setattr(
        bench_transpilers_cmd, "cli_transpilers", lambda: {"python": Transpilador}
    )

    assert BenchTranspilersCommand.requires_sqlite_key is False
    resultado = BenchTranspilersCommand().run(
        SimpleNamespace(output=None, profile=False, perfil="publico")
    )

    assert resultado == 0
    assert len(capturados) == len(bench_transpilers_cmd.VALID_SIZES)
    assert all(type(_valor_asignado(ast[1])) is NodoInstancia for ast in capturados)


def test_parser_incremental_conserva_contrato_sintactico(
    monkeypatch, base_datos_temporal
):
    codigo = "clase Persona:\nfin\nvar persona = Persona()"
    tokens = Lexer(codigo).analizar_token()

    ast = Parser(tokens).parsear(incremental=True)

    assert type(_valor_asignado(ast[1])) is NodoLlamadaFuncion


def test_carga_modulo_usa_ast_resuelto(tmp_path):
    modulo = tmp_path / "persona.cobra"
    modulo.write_text(
        "clase Persona:\nfin\nvar persona = Persona()", encoding="utf-8"
    )

    ast = cargar_ast_modulo(
        str(modulo), modules_path=str(tmp_path), whitelist={str(tmp_path)}
    )

    assert type(_valor_asignado(ast[1])) is NodoInstancia


def test_clase_sin_argumentos_produce_instancia():
    ast = _parsear("clase Vacia:\nfin\nvar x = Vacia()")

    assert type(ast[0]) is NodoClase
    instancia = _valor_asignado(ast[1])
    assert type(instancia) is NodoInstancia
    assert instancia.nombre_clase == "Vacia"
    assert instancia.argumentos == []


def test_clase_con_un_argumento_preserva_valor_y_tipo():
    ast = _parsear(
        'clase Persona:\n'
        '    metodo inicializar(este, nombre):\n'
        '        imprimir nombre\n'
        'fin\n'
        'var persona = Persona("Adolfo")'
    )

    instancia = _valor_asignado(ast[1])
    assert type(instancia) is NodoInstancia
    assert instancia.nombre_clase == "Persona"
    assert len(instancia.argumentos) == 1
    assert type(instancia.argumentos[0]) is NodoValor
    assert instancia.argumentos[0].valor == "Adolfo"


def test_clase_con_varios_argumentos_preserva_orden_y_tipos():
    ast = _parsear(
        "clase Punto:\n"
        "    metodo inicializar(este, x, y):\n"
        "        imprimir x\n"
        "fin\n"
        "var p = Punto(1, 2)"
    )

    instancia = _valor_asignado(ast[1])
    assert type(instancia) is NodoInstancia
    assert instancia.nombre_clase == "Punto"
    assert [type(arg) for arg in instancia.argumentos] == [NodoValor, NodoValor]
    assert [arg.valor for arg in instancia.argumentos] == [1, 2]


def test_funcion_normal_permanece_llamada_funcion():
    ast = _parsear(
        "func procesar(x):\n"
        "    retornar x\n"
        "fin\n"
        "var resultado = procesar(1)"
    )

    llamada = _valor_asignado(ast[1])
    assert type(llamada) is NodoLlamadaFuncion
    assert llamada.nombre == "procesar"
    assert type(llamada.argumentos[0]) is NodoValor


def test_clase_y_funcion_resuelven_cada_nombre_a_su_nodo():
    ast = _parsear(
        "clase Persona:\nfin\n"
        "func procesar(x):\n"
        "    retornar x\n"
        "fin\n"
        'var persona = Persona("Adolfo")\n'
        'var resultado = procesar("Adolfo")'
    )

    assert type(_valor_asignado(ast[2])) is NodoInstancia
    assert type(_valor_asignado(ast[3])) is NodoLlamadaFuncion


def test_instancia_y_llamada_postfix_son_expresiones_distintas():
    ast = _parsear(
        "clase Persona:\n"
        "    metodo saludar(este):\n"
        '        imprimir "Hola"\n'
        "fin\n"
        'var persona = Persona("Adolfo")\n'
        "persona.saludar()"
    )

    assert type(_valor_asignado(ast[1])) is NodoInstancia
    llamada = ast[2]
    assert type(llamada) is NodoLlamadaMetodo
    assert type(llamada.objeto) is NodoIdentificador
    assert llamada.objeto.nombre == "persona"
    assert llamada.nombre_metodo == "saludar"
    assert llamada.argumentos == []


def test_referencia_hacia_delante_no_se_resuelve_como_instancia():
    ast = _parsear("var x = Posterior()\nclase Posterior:\nfin")

    assert type(_valor_asignado(ast[0])) is NodoLlamadaFuncion


def test_colision_clase_funcion_no_inventa_precedencia():
    ast = _parsear(
        "clase Duplicado:\nfin\n"
        "func Duplicado():\n"
        "    retornar 1\n"
        "fin\n"
        "var x = Duplicado()"
    )

    assert type(_valor_asignado(ast[2])) is NodoLlamadaFuncion
