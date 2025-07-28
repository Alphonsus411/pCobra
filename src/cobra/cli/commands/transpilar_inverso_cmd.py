import os
from typing import Any, Optional
from argparse import _SubParsersAction

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
    """Convierte código desde otro lenguaje a Cobra y luego a otro lenguaje.
    
    Esta clase implementa un comando que permite transpilar código desde un lenguaje
    de origen a un lenguaje de destino, pasando por una representación intermedia
    en el AST de Cobra.
    """

    name: str = "transpilar-inverso"

    def register_subparser(self, subparsers: _SubParsersAction) -> Any:
        """Registra los argumentos del subcomando en el parser.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            Parser configurado para el subcomando
        """
        parser = subparsers.add_parser(
            self.name, help=_("Transpila desde un lenguaje origen a otro destino")
        )
        parser.add_argument(
            "archivo",
            help=_("Ruta al archivo fuente a transpilar")
        )
        parser.add_argument(
            "--origen",
            choices=ORIGIN_CHOICES,
            help=_("Lenguaje de origen del código fuente"),
            required=True
        )
        parser.add_argument(
            "--destino",
            choices=LANG_CHOICES,
            help=_("Lenguaje de destino para la transpilación"),
            required=True
        )
        parser.set_defaults(cmd=self)
        return parser

    def _validar_archivo(self, archivo: str) -> Optional[str]:
        """Valida que el archivo exista y sea legible.
        
        Args:
            archivo: Ruta al archivo a validar
            
        Returns:
            Mensaje de error si hay problemas, None si todo está bien
        """
        if not os.path.exists(archivo):
            return f"El archivo '{archivo}' no existe"
        if not os.path.isfile(archivo):
            return f"'{archivo}' no es un archivo regular"
        if not os.access(archivo, os.R_OK):
            return f"No hay permisos de lectura para '{archivo}'"
        return None

    def run(self, args: Any) -> int:
        """Ejecuta la transpilación del código.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            0 si la ejecución fue exitosa, otro valor en caso de error
        """
        # Validar archivo
        if error := self._validar_archivo(args.archivo):
            mostrar_error(error)
            return 1

        # Validar transpiladores
        reverse_cls = REVERSE_TRANSPILERS.get(args.origen)
        if reverse_cls is None:
            mostrar_error(f"Transpilador de origen '{args.origen}' no soportado")
            return 1

        transp_cls = TRANSPILERS.get(args.destino)
        if transp_cls is None:
            mostrar_error(f"Transpilador de destino '{args.destino}' no soportado")
            return 1

        # Leer y validar contenido del archivo
        try:
            with open(args.archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                if not contenido.strip():
                    mostrar_error(f"El archivo '{args.archivo}' está vacío")
                    return 1
        except UnicodeDecodeError:
            mostrar_error(f"Error de codificación al leer '{args.archivo}'")
            return 1
        except OSError as exc:
            mostrar_error(f"Error al leer el archivo: {exc}")
            return 1

        # Transpilar código
        try:
            ast = reverse_cls().load_file(args.archivo)
        except NotImplementedError:
            mostrar_error(f"El transpilador de {args.origen} no está implementado completamente")
            return 1
        except Exception as exc:
            mostrar_error(f"Error al convertir desde {args.origen}: {exc}")
            return 1

        try:
            codigo = transp_cls().generate_code(ast)
            mostrar_info(
                _("Código transpilado ({name}):").format(name=transp_cls.__name__)
            )
            print(codigo)
            return 0
        except Exception as exc:
            mostrar_error(f"Error generando código {args.destino}: {exc}")
            return 1