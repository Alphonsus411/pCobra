import os

from cobra.transpilers.reverse import (
    ReverseFromPython,
    ReverseFromC,
    ReverseFromCPP,
    ReverseFromJS,
    ReverseFromJava,
    ReverseFromGo,
    ReverseFromJulia,
    ReverseFromPHP,
    ReverseFromPerl,
    ReverseFromR,
    ReverseFromRuby,
    ReverseFromRust,
    ReverseFromSwift,
    ReverseFromKotlin,
    ReverseFromFortran,
    ReverseFromASM,
    ReverseFromCOBOL,
    ReverseFromLatex,
    ReverseFromMatlab,
    ReverseFromMojo,
    ReverseFromPascal,
    ReverseFromVisualBasic,
    ReverseFromWasm,
)
from cobra.cli.commands.base import BaseCommand
from cobra.cli.commands.compile_cmd import TRANSPILERS, LANG_CHOICES
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info

REVERSE_TRANSPILERS = {
    "python": ReverseFromPython,
    "c": ReverseFromC,
    "cpp": ReverseFromCPP,
    "js": ReverseFromJS,
    "java": ReverseFromJava,
    "go": ReverseFromGo,
    "julia": ReverseFromJulia,
    "php": ReverseFromPHP,
    "perl": ReverseFromPerl,
    "r": ReverseFromR,
    "ruby": ReverseFromRuby,
    "rust": ReverseFromRust,
    "swift": ReverseFromSwift,
    "kotlin": ReverseFromKotlin,
    "fortran": ReverseFromFortran,
    "asm": ReverseFromASM,
    "cobol": ReverseFromCOBOL,
    "latex": ReverseFromLatex,
    "matlab": ReverseFromMatlab,
    "mojo": ReverseFromMojo,
    "pascal": ReverseFromPascal,
    "visualbasic": ReverseFromVisualBasic,
    "wasm": ReverseFromWasm,
}

ORIGIN_CHOICES = sorted(REVERSE_TRANSPILERS.keys())


class TranspilarInversoCommand(BaseCommand):
    """Convierte código desde otro lenguaje a Cobra y luego a otro lenguaje."""

    name = "transpilar-inverso"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(
            self.name, help=_("Transpila desde un lenguaje origen a otro destino")
        )
        parser.add_argument("archivo")
        parser.add_argument(
            "--origen",
            choices=ORIGIN_CHOICES,
            default="python",
            help=_("Lenguaje de origen"),
        )
        parser.add_argument(
            "--destino",
            choices=LANG_CHOICES,
            default="python",
            help=_("Lenguaje de destino"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def run(self, args):
        archivo = args.archivo
        if not os.path.exists(archivo):
            mostrar_error(f"El archivo '{archivo}' no existe")
            return 1

        reverse_cls = REVERSE_TRANSPILERS.get(args.origen)
        transp_cls = TRANSPILERS.get(args.destino)
        if reverse_cls is None or transp_cls is None:
            mostrar_error("Transpilador no soportado")
            return 1

        try:
            ast = reverse_cls().load_file(archivo)
        except Exception as exc:  # pylint: disable=broad-except
            mostrar_error(f"Error al convertir {args.origen}: {exc}")
            return 1

        try:
            codigo = transp_cls().generate_code(ast)
            mostrar_info(
                _("Código transpilado ({name}):").format(name=transp_cls.__name__)
            )
            print(codigo)
            return 0
        except Exception as exc:  # pylint: disable=broad-except
            mostrar_error(f"Error generando código: {exc}")
            return 1
