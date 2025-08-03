import os
import logging
from typing import Optional, Dict, Type
from argparse import _SubParsersAction, ArgumentParser, Namespace
from contextlib import contextmanager
from enum import Enum
from chardet import detect
from jsonschema import ValidationError

from cobra.transpilers.reverse import (
    ReverseFromPython, ReverseFromC, ReverseFromCPP, ReverseFromJS,
    ReverseFromJava, ReverseFromGo, ReverseFromJulia, ReverseFromPHP,
    ReverseFromPerl, ReverseFromR, ReverseFromRuby, ReverseFromRust,
    ReverseFromSwift, ReverseFromKotlin, ReverseFromFortran, ReverseFromASM,
    ReverseFromCOBOL, ReverseFromLatex, ReverseFromMatlab, ReverseFromMojo,
    ReverseFromPascal, ReverseFromVisualBasic, ReverseFromWasm
)
from cobra.cli.commands.base import BaseCommand, CommandError
from cobra.cli.commands.compile_cmd import TRANSPILERS, LANG_CHOICES
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info

# Configuración del logging
logger = logging.getLogger(__name__)

# Constantes
MAX_FILE_SIZE = 1024 * 1024  # 1MB
EXTENSIONES_POR_LENGUAJE: Dict[str, str] = {
    "python": ".py",
    "c": ".c",
    "cpp": ".cpp",
    "js": ".js",
    "java": ".java",
    # Añadir más extensiones según sea necesario
}

class UnsupportedLanguageError(Exception):
    """Error lanzado cuando se intenta usar un lenguaje no soportado."""
    pass

class TranspilationError(Exception):
    """Error lanzado cuando ocurre un problema durante la transpilación."""
    pass

class SourceLanguage(str, Enum):
    """Lenguajes de origen soportados para transpilación."""
    PYTHON = "python"
    C = "c"
    CPP = "cpp"
    JS = "js"
    JAVA = "java"
    GO = "go"
    JULIA = "julia"
    PHP = "php"
    PERL = "perl"
    R = "r"
    RUBY = "ruby"
    RUST = "rust"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    FORTRAN = "fortran"
    ASM = "asm"
    COBOL = "cobol"
    LATEX = "latex"
    MATLAB = "matlab"
    MOJO = "mojo"
    PASCAL = "pascal"
    VISUALBASIC = "visualbasic"
    WASM = "wasm"

REVERSE_TRANSPILERS: Dict[SourceLanguage, Type] = {
    SourceLanguage.PYTHON: ReverseFromPython,
    SourceLanguage.C: ReverseFromC,
    SourceLanguage.CPP: ReverseFromCPP,
    SourceLanguage.JS: ReverseFromJS,
    SourceLanguage.JAVA: ReverseFromJava,
    SourceLanguage.GO: ReverseFromGo,
    SourceLanguage.JULIA: ReverseFromJulia,
    SourceLanguage.PHP: ReverseFromPHP,
    SourceLanguage.PERL: ReverseFromPerl,
    SourceLanguage.R: ReverseFromR,
    SourceLanguage.RUBY: ReverseFromRuby,
    SourceLanguage.RUST: ReverseFromRust,
    SourceLanguage.SWIFT: ReverseFromSwift,
    SourceLanguage.KOTLIN: ReverseFromKotlin,
    SourceLanguage.FORTRAN: ReverseFromFortran,
    SourceLanguage.ASM: ReverseFromASM,
    SourceLanguage.COBOL: ReverseFromCOBOL,
    SourceLanguage.LATEX: ReverseFromLatex,
    SourceLanguage.MATLAB: ReverseFromMatlab,
    SourceLanguage.MOJO: ReverseFromMojo,
    SourceLanguage.PASCAL: ReverseFromPascal,
    SourceLanguage.VISUALBASIC: ReverseFromVisualBasic,
    SourceLanguage.WASM: ReverseFromWasm,
}

ORIGIN_CHOICES = sorted(lang.value for lang in SourceLanguage)

@contextmanager
def archivo_fuente(ruta: str, codificacion: str):
    """Context manager para manejar la apertura y cierre de archivos.
    
    Args:
        ruta: Ruta al archivo
        codificacion: Codificación del archivo
        
    Yields:
        El archivo abierto
        
    Raises:
        OSError: Si hay problemas al abrir el archivo
    """
    try:
        with open(ruta, 'r', encoding=codificacion) as f:
            yield f
    except Exception as e:
        logger.error(f"Error al leer archivo: {e}")
        raise

class TranspilarInversoCommand(BaseCommand):
    """Convierte código desde otro lenguaje a Cobra y luego a otro lenguaje.
    
    Esta clase implementa un comando que permite transpilar código desde un lenguaje
    de origen a un lenguaje de destino, pasando por una representación intermedia
    en el AST de Cobra.
    """

    name: str = "transpilar-inverso"

    def register_subparser(self, subparsers: _SubParsersAction) -> ArgumentParser:
        """Registra los argumentos del subcomando en el parser.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            ArgumentParser: Parser configurado para el subcomando
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
            required=True,
            type=SourceLanguage
        )
        parser.add_argument(
            "--destino",
            choices=LANG_CHOICES,
            help=_("Lenguaje de destino para la transpilación"),
            required=True
        )
        parser.set_defaults(cmd=self)
        return parser

    def _validar_archivo(self, archivo: str, lenguaje: str) -> Optional[str]:
        """Valida que el archivo exista y sea legible.
        
        Args:
            archivo: Ruta al archivo a validar
            lenguaje: Lenguaje de origen esperado
            
        Returns:
            Optional[str]: Mensaje de error si hay problemas, None si todo está bien
        """
        if not os.path.exists(archivo):
            return f"El archivo '{archivo}' no existe"
        if not os.path.isfile(archivo):
            return f"'{archivo}' no es un archivo regular"
        if not os.access(archivo, os.R_OK):
            return f"No hay permisos de lectura para '{archivo}'"
        if os.path.getsize(archivo) > MAX_FILE_SIZE:
            return f"El archivo '{archivo}' excede el tamaño máximo permitido ({MAX_FILE_SIZE} bytes)"
            
        extension_esperada = EXTENSIONES_POR_LENGUAJE.get(lenguaje)
        if extension_esperada and not archivo.lower().endswith(extension_esperada):
            return f"El archivo '{archivo}' no tiene la extensión esperada para {lenguaje} ({extension_esperada})"
        
        return None

    def _detectar_codificacion(self, archivo: str) -> str:
        """Detecta la codificación del archivo.
        
        Args:
            archivo: Ruta al archivo
            
        Returns:
            str: Codificación detectada
        """
        with open(archivo, 'rb') as f:
            raw_data = f.read()
        resultado = detect(raw_data)
        encoding = resultado['encoding']
        if not encoding:
            logger.warning(f"No se pudo detectar la codificación para {archivo}, usando utf-8")
            encoding = 'utf-8'
        return encoding

    def _verificar_dependencias(self, origen: str, destino: str) -> None:
        """Verifica que los transpiladores necesarios estén disponibles.
        
        Args:
            origen: Lenguaje de origen
            destino: Lenguaje de destino
            
        Raises:
            UnsupportedLanguageError: Si algún transpilador no está disponible
        """
        if origen not in REVERSE_TRANSPILERS:
            raise UnsupportedLanguageError(f"Transpilador de origen '{origen}' no disponible")
        if destino not in TRANSPILERS:
            raise UnsupportedLanguageError(f"Transpilador de destino '{destino}' no disponible")

    def run(self, args: Namespace) -> int:
        """Ejecuta la transpilación del código.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: 0 si la ejecución fue exitosa, otro valor en caso de error
            
        Raises:
            CommandError: Si hay errores en la validación o transpilación
        """
        try:
            logger.debug(f"Iniciando validación del archivo {args.archivo}")
            
            # Validar archivo
            if error := self._validar_archivo(args.archivo, args.origen):
                raise CommandError(error)

            # Verificar dependencias
            self._verificar_dependencias(args.origen, args.destino)

            # Validar transpiladores
            reverse_cls = REVERSE_TRANSPILERS.get(args.origen)
            transp_cls = TRANSPILERS.get(args.destino)
            
            logger.debug(f"Usando transpilador {reverse_cls.__name__} para origen {args.origen}")
            logger.debug(f"Usando transpilador {transp_cls.__name__} para destino {args.destino}")

            # Detectar codificación y leer archivo
            codificacion = self._detectar_codificacion(args.archivo)
            logger.debug(f"Codificación detectada para {args.archivo}: {codificacion}")

            with archivo_fuente(args.archivo, codificacion) as f:
                contenido = f.read()
                if not contenido.strip():
                    raise ValidationError(f"El archivo '{args.archivo}' está vacío")

            # Transpilar código
            logger.info(f"Iniciando transpilación de {args.origen} a {args.destino}")
            ast = reverse_cls().load_file(args.archivo)
            codigo = transp_cls().generate_code(ast)
            
            mostrar_info(_("Código transpilado ({name}):").format(name=transp_cls.__name__))
            print(codigo)
            return 0

        except (UnicodeDecodeError, UnicodeError) as exc:
            logger.error(f"Error de codificación: {exc}", exc_info=True)
            mostrar_error(f"Error de codificación al leer '{args.archivo}'")
            return 1
        except OSError as exc:
            logger.error(f"Error de E/S: {exc}", exc_info=True)
            mostrar_error(f"Error al leer el archivo: {exc}")
            return 1
        except NotImplementedError:
            logger.error(f"Transpilador no implementado: {args.origen}")
            mostrar_error(f"El transpilador de {args.origen} no está implementado completamente")
            return 1
        except (CommandError, ValidationError, UnsupportedLanguageError) as exc:
            mostrar_error(str(exc))
            return 1
        except TranspilationError as exc:
            logger.error(f"Error en transpilación: {exc}", exc_info=True)
            mostrar_error(f"Error al transpilar el código: {exc}")
            return 1
        except Exception as exc:
            logger.error(f"Error inesperado: {exc}", exc_info=True)
            mostrar_error(f"Error inesperado: {exc}")
            return 1