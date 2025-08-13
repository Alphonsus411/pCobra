import logging
import multiprocessing
import os
from importlib import import_module
from importlib.metadata import entry_points

from argcomplete.completers import FilesCompleter

from cobra.transpilers import module_map
from cobra.transpilers.transpiler.to_asm import TranspiladorASM
from cobra.transpilers.transpiler.to_c import TranspiladorC
from cobra.transpilers.transpiler.to_cobol import TranspiladorCOBOL
from cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from cobra.transpilers.transpiler.to_fortran import TranspiladorFortran
from cobra.transpilers.transpiler.to_go import TranspiladorGo
from cobra.transpilers.transpiler.to_java import TranspiladorJava
from cobra.transpilers.transpiler.to_kotlin import TranspiladorKotlin
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.transpiler.to_julia import TranspiladorJulia
from cobra.transpilers.transpiler.to_latex import TranspiladorLatex
from cobra.transpilers.transpiler.to_llvm import TranspiladorLLVM
from cobra.transpilers.transpiler.to_matlab import TranspiladorMatlab
from cobra.transpilers.transpiler.to_mojo import TranspiladorMojo
from cobra.transpilers.transpiler.to_pascal import TranspiladorPascal
from cobra.transpilers.transpiler.to_php import TranspiladorPHP
from cobra.transpilers.transpiler.to_perl import TranspiladorPerl
from cobra.transpilers.transpiler.to_visualbasic import TranspiladorVisualBasic
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.transpilers.transpiler.to_r import TranspiladorR
from cobra.transpilers.transpiler.to_ruby import TranspiladorRuby
from cobra.transpilers.transpiler.to_rust import TranspiladorRust
from cobra.transpilers.transpiler.to_wasm import TranspiladorWasm
from cobra.transpilers.transpiler.to_swift import TranspiladorSwift
from core.ast_cache import obtener_ast
from core.sandbox import validar_dependencias
from core.semantic_validators import (
    PrimitivaPeligrosaError,
    construir_cadena,
)
from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info
from cobra.cli.utils.validators import validar_archivo_existente
from cobra.core import ParserError
from core.cobra_config import tiempo_max_transpilacion

# Constantes de configuración
MAX_PROCESSES = 4
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
PROCESS_TIMEOUT = tiempo_max_transpilacion()
MAX_LANGUAGES = 10

TRANSPILERS = {
    "python": TranspiladorPython,
    "js": TranspiladorJavaScript,
    "asm": TranspiladorASM,
    "rust": TranspiladorRust,
    "cpp": TranspiladorCPP,
    "c": TranspiladorC,
    "go": TranspiladorGo,
    "kotlin": TranspiladorKotlin,
    "swift": TranspiladorSwift,
    "ruby": TranspiladorRuby,
    "r": TranspiladorR,
    "julia": TranspiladorJulia,
    "java": TranspiladorJava,
    "cobol": TranspiladorCOBOL,
    "fortran": TranspiladorFortran,
    "pascal": TranspiladorPascal,
    "php": TranspiladorPHP,
    "perl": TranspiladorPerl,
    "visualbasic": TranspiladorVisualBasic,
    "matlab": TranspiladorMatlab,
    "mojo": TranspiladorMojo,
    "latex": TranspiladorLatex,
    "llvm": TranspiladorLLVM,
    "wasm": TranspiladorWasm,
}

# Cargar transpiladores externos
try:
    eps = entry_points(group="cobra.transpilers")
except TypeError:  # Compatibilidad con versiones antiguas
    eps = entry_points().get("cobra.transpilers", [])

for ep in eps:
    try:
        module_name, class_name = ep.value.split(":", 1)
        if not all(c.isalnum() or c in "._" for c in module_name + class_name):
            logging.warning(f"Nombre de módulo o clase inválido: {ep.value}")
            continue
        cls = getattr(import_module(module_name), class_name)
        TRANSPILERS[ep.name] = cls
    except Exception as exc:
        logging.error("Error cargando transpilador %s: %s", ep.name, exc)

LANG_CHOICES = sorted(TRANSPILERS.keys())

def validate_file(filepath: str) -> bool:
    """Valida que el archivo sea accesible y cumpla con los límites establecidos."""
    try:
        path = validar_archivo_existente(filepath)
    except FileNotFoundError:
        raise ValueError(f"'{filepath}' no es un archivo válido")
    if not os.access(path, os.R_OK):
        raise ValueError(f"No hay permisos de lectura para '{filepath}'")
    if os.path.getsize(path) > MAX_FILE_SIZE:
        raise ValueError(f"El archivo excede el tamaño máximo permitido ({MAX_FILE_SIZE} bytes)")
    return True

def run_transpiler_pool(languages: list, ast, executor) -> list:
    """Ejecuta los transpiladores en paralelo con límites de seguridad."""
    if len(languages) > MAX_LANGUAGES:
        raise ValueError(_("Demasiados lenguajes especificados"))
    with multiprocessing.Pool(processes=min(len(languages), MAX_PROCESSES)) as pool:
        return pool.map_async(
            executor,
            [(lang, ast) for lang in languages],
            timeout=PROCESS_TIMEOUT
        ).get(timeout=PROCESS_TIMEOUT)

class CompileCommand(BaseCommand):
    """Transpila un archivo Cobra a distintos lenguajes."""

    name = "compilar"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Transpila un archivo"))
        parser.add_argument("archivo").completer = FilesCompleter()
        parser.add_argument(
            "--tipo",
            choices=LANG_CHOICES,
            default="python",
            help=_("Tipo de código generado"),
        )
        parser.add_argument(
            "--backend",
            choices=LANG_CHOICES,
            help=_("Alias de --tipo"),
        )
        parser.add_argument(
            "--tipos",
            help=_("Lista de lenguajes separados por comas"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def _ejecutar_transpilador(self, parametros: tuple) -> tuple:
        """Ejecuta un transpilador específico."""
        lang, ast = parametros
        transp = TRANSPILERS[lang]()
        return lang, transp.__class__.__name__, transp.generate_code(ast)

    def run(self, args):
        """Ejecuta la lógica del comando."""
        archivo = args.archivo
        
        try:
            validate_file(archivo)
        except ValueError as e:
            mostrar_error(str(e))
            return 1

        mod_info = module_map.get_toml_map()
        try:
            if getattr(args, "tipos", None):
                langs = [t.strip() for t in args.tipos.split(",") if t.strip()]
                for lang in langs:
                    validar_dependencias(lang, mod_info)
            else:
                validar_dependencias(args.tipo, mod_info)
        except (ValueError, FileNotFoundError) as dep_err:
            mostrar_error(f"Error de dependencias: {dep_err}")
            return 1

        try:
            with open(archivo, "r", encoding="utf-8") as f:
                codigo = f.read()

            ast = obtener_ast(codigo)
            validador = construir_cadena()
            for nodo in ast:
                nodo.aceptar(validador)

            if getattr(args, "tipos", None):
                lenguajes = [t.strip() for t in args.tipos.split(",") if t.strip()]
                for lang in lenguajes:
                    if lang not in TRANSPILERS:
                        raise ValueError(_("Transpilador no soportado."))
                
                try:
                    resultados = run_transpiler_pool(lenguajes, ast, self._ejecutar_transpilador)
                    for lang, nombre, resultado in resultados:
                        mostrar_info(
                            _("Código generado ({nombre}) para {lang}:").format(
                                nombre=nombre, lang=lang
                            )
                        )
                        print(resultado)
                except multiprocessing.TimeoutError:
                    mostrar_error(_("Tiempo de ejecución excedido"))
                    return 1
            else:
                transpilador = args.tipo if not getattr(args, "backend", None) else args.backend
                if transpilador not in TRANSPILERS:
                    raise ValueError(_("Transpilador no soportado."))
                transp = TRANSPILERS[transpilador]()
                resultado = transp.generate_code(ast)
                mostrar_info(
                    _("Código generado ({name}):").format(
                        name=transp.__class__.__name__
                    )
                )
                print(resultado)
            return 0

        except PrimitivaPeligrosaError as pe:
            logging.error("Primitiva peligrosa: %s", pe)
            mostrar_error(str(pe))
            return 1
        except ParserError as se:
            logging.error("Error de sintaxis durante la transpilación: %s", se)
            mostrar_error(f"Error durante la transpilación: {se}")
            return 1
        except Exception as e:
            logging.error("Error general durante la transpilación: %s", e)
            mostrar_error(str(e))
            return 1