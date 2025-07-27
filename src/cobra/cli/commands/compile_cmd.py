import logging
import multiprocessing
import os
from importlib import import_module
from importlib.metadata import entry_points

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

# Mapa que asocia el nombre de cada lenguaje con la clase de su
# transpilador. Sirve como una fábrica sencilla: a partir de una clave
# se puede instanciar el transpilador adecuado. Este diccionario se
# amplía dinámicamente con los transpiladores registrados mediante
# ``entry_points`` en el grupo ``cobra.transpilers``.
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
    "wasm": TranspiladorWasm,
}

# Detectar transpiladores externos registrados via entry points
try:
    eps = entry_points(group="cobra.transpilers")
except TypeError:  # Compatibilidad con versiones antiguas
    eps = entry_points().get("cobra.transpilers", [])

for ep in eps:
    try:
        module_name, class_name = ep.value.split(":", 1)
        cls = getattr(import_module(module_name), class_name)
        TRANSPILERS[ep.name] = cls
    except Exception as exc:  # pylint: disable=broad-except
        logging.error("Error cargando transpilador %s: %s", ep.name, exc)

LANG_CHOICES = sorted(TRANSPILERS.keys())


class CompileCommand(BaseCommand):
    """Transpila un archivo Cobra a distintos lenguajes.

    Soporta Python, JavaScript, ensamblador, Rust, C++, C, Go, Kotlin, Swift,
    R, Julia, Ruby, PHP, Java y ahora también COBOL, Fortran, Pascal,
    VisualBasic, Matlab, Mojo, LaTeX y WebAssembly.
    """

    name = "compilar"

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Transpila un archivo"))
        parser.add_argument("archivo")
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
        lang, ast = parametros
        transp = TRANSPILERS[lang]()
        return lang, transp.__class__.__name__, transp.generate_code(ast)

    def run(self, args):
        """Ejecuta la lógica del comando."""
        archivo = args.archivo
        if getattr(args, "backend", None):
            args.tipo = args.backend
        if not os.path.isfile(archivo):
            mostrar_error(f"'{archivo}' no es un archivo válido")
            return 1
        if not os.access(archivo, os.R_OK):
            mostrar_error(f"No hay permisos de lectura para '{archivo}'")
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
        except UnicodeDecodeError as ude:
            mostrar_error(f"Error de codificación en archivo: {ude}")
            return 1
        try:
            ast = obtener_ast(codigo)
            validador = construir_cadena()
            for nodo in ast:
                nodo.aceptar(validador)

            if getattr(args, "tipos", None):
                lenguajes = [t.strip() for t in args.tipos.split(",") if t.strip()]
                for lang in lenguajes:
                    if lang not in TRANSPILERS:
                        raise ValueError(_("Transpilador no soportado."))
                # Agregar límite de procesos
                MAX_PROCESSES = 4
                with multiprocessing.Pool(processes=min(len(lenguajes), MAX_PROCESSES)) as pool:
                    resultados = pool.map(
                        self._ejecutar_transpilador, [(lang, ast) for lang in lenguajes]
                    )
                for lang, nombre, resultado in resultados:
                    mostrar_info(
                        _("Código generado ({nombre}) para {lang}:").format(
                            nombre=nombre, lang=lang
                        )
                    )
                    print(resultado)
                return 0
            else:
                transpilador = args.tipo
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
            logging.error(f"Primitiva peligrosa: {pe}")
            mostrar_error(str(pe))
            return 1
        except SyntaxError as se:
            logging.error(f"Error de sintaxis durante la transpilación: {se}")
            mostrar_error(f"Error durante la transpilación: {se}")
            return 1
        except Exception as e:
            logging.error(f"Error general durante la transpilación: {e}")
            mostrar_error(f"Error durante la transpilación: {e}")
            return 1