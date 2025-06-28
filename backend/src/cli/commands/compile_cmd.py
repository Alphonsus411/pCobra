import logging
import os
import multiprocessing
from .base import BaseCommand
from ..i18n import _
from ..utils.messages import mostrar_error, mostrar_info
from backend.src.cobra.transpilers import module_map
from backend.src.core.sandbox import validar_dependencias

from backend.src.core.ast_cache import obtener_ast
from backend.src.core.semantic_validators import PrimitivaPeligrosaError, construir_cadena
from backend.src.cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from backend.src.cobra.transpilers.transpiler.to_python import TranspiladorPython
from backend.src.cobra.transpilers.transpiler.to_asm import TranspiladorASM
from backend.src.cobra.transpilers.transpiler.to_rust import TranspiladorRust
from backend.src.cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from backend.src.cobra.transpilers.transpiler.to_c import TranspiladorC
from backend.src.cobra.transpilers.transpiler.to_go import TranspiladorGo
from backend.src.cobra.transpilers.transpiler.to_r import TranspiladorR
from backend.src.cobra.transpilers.transpiler.to_julia import TranspiladorJulia
from backend.src.cobra.transpilers.transpiler.to_ruby import TranspiladorRuby
from backend.src.cobra.transpilers.transpiler.to_java import TranspiladorJava
from backend.src.cobra.transpilers.transpiler.to_cobol import TranspiladorCOBOL
from backend.src.cobra.transpilers.transpiler.to_fortran import TranspiladorFortran
from backend.src.cobra.transpilers.transpiler.to_pascal import TranspiladorPascal
from backend.src.cobra.transpilers.transpiler.to_php import TranspiladorPHP
from backend.src.cobra.transpilers.transpiler.to_matlab import TranspiladorMatlab
from backend.src.cobra.transpilers.transpiler.to_latex import TranspiladorLatex
from backend.src.cobra.transpilers.transpiler.to_wasm import TranspiladorWasm

TRANSPILERS = {
    "python": TranspiladorPython,
    "js": TranspiladorJavaScript,
    "asm": TranspiladorASM,
    "rust": TranspiladorRust,
    "cpp": TranspiladorCPP,
    "c": TranspiladorC,
    "go": TranspiladorGo,
    "ruby": TranspiladorRuby,
    "r": TranspiladorR,
    "julia": TranspiladorJulia,
    "java": TranspiladorJava,
    "cobol": TranspiladorCOBOL,
    "fortran": TranspiladorFortran,
    "pascal": TranspiladorPascal,
    "php": TranspiladorPHP,
    "matlab": TranspiladorMatlab,
    "latex": TranspiladorLatex,
    "wasm": TranspiladorWasm,
}


class CompileCommand(BaseCommand):
    """Transpila un archivo Cobra a distintos lenguajes.

    Soporta Python, JavaScript, ensamblador, Rust, C++, C, Go, R, Julia, Ruby,
    PHP, Java y ahora también COBOL, Fortran, Pascal, Matlab, LaTeX y WebAssembly.
    """

    name = "compilar"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help=_("Transpila un archivo"))
        parser.add_argument("archivo")
        parser.add_argument(
            "--tipo",
            choices=[
                "python",
                "js",
                "asm",
                "rust",
                "cpp",
                "c",
                "go",
                "ruby",
                "r",
                "julia",
                "java",
                "cobol",
                "fortran",
                "pascal",
                "php",
                "matlab",
                "latex",
                "wasm",
            ],
            default="python",
            help=_("Tipo de código generado"),
        )
        parser.add_argument(
            "--backend",
            choices=[
                "python",
                "js",
                "asm",
                "rust",
                "cpp",
                "c",
                "go",
                "ruby",
                "r",
                "julia",
                "java",
                "cobol",
                "fortran",
                "pascal",
                "php",
                "matlab",
                "latex",
                "wasm",
            ],
            help=_("Alias de --tipo"),
        )
        parser.add_argument(
            "--tipos",
            help=_("Lista de lenguajes separados por comas"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def _ejecutar_transpilador(self, parametros):
        lang, ast = parametros
        transp = TRANSPILERS[lang]()
        return lang, transp.__class__.__name__, transp.transpilar(ast)

    def run(self, args):
        archivo = args.archivo
        if getattr(args, "backend", None):
            args.tipo = args.backend
        if not os.path.exists(archivo):
            mostrar_error(f"El archivo '{archivo}' no existe")
            return 1

        mod_info = module_map.get_toml_map()
        try:
            if getattr(args, "tipos", None):
                langs = [t.strip() for t in args.tipos.split(',') if t.strip()]
                for lang in langs:
                    validar_dependencias(lang, mod_info)
            else:
                validar_dependencias(args.tipo, mod_info)
        except (ValueError, FileNotFoundError) as dep_err:
            mostrar_error(f"Error de dependencias: {dep_err}")
            return 1

        with open(archivo, "r") as f:
            codigo = f.read()
        try:
            ast = obtener_ast(codigo)
            validador = construir_cadena()
            for nodo in ast:
                nodo.aceptar(validador)

            if getattr(args, "tipos", None):
                lenguajes = [t.strip() for t in args.tipos.split(',') if t.strip()]
                for l in lenguajes:
                    if l not in TRANSPILERS:
                        raise ValueError(_("Transpilador no soportado."))
                with multiprocessing.Pool(processes=len(lenguajes)) as pool:
                    resultados = pool.map(self._ejecutar_transpilador, [(l, ast) for l in lenguajes])
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
                resultado = transp.transpilar(ast)
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
