import inspect
import logging
import os
from argparse import ArgumentParser, Namespace
from contextlib import contextmanager
from typing import Any, Dict, Optional, Type

try:  # pragma: no cover - dependencia opcional
    from chardet import detect as _detect_encoding
except ModuleNotFoundError:  # pragma: no cover - entornos sin chardet
    _detect_encoding = None

try:  # pragma: no cover - dependencia opcional
    from jsonschema import ValidationError as _JSONSchemaValidationError
except ModuleNotFoundError:  # pragma: no cover - entornos sin jsonschema
    _JSONSchemaValidationError = None
    class _FallbackValidationError(RuntimeError):
        """Excepción básica usada cuando falta jsonschema."""

        pass
else:
    class _FallbackValidationError(_JSONSchemaValidationError):  # type: ignore[misc]
        pass

ValidationError = _FallbackValidationError

import pcobra.cobra.transpilers.reverse as reverse_module
from pcobra.cobra.cli.commands.base import BaseCommand, CommandError
from pcobra.cobra.cli.commands.compile_cmd import TRANSPILERS
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.utils.validators import validar_archivo_existente

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
REVERSE_TRANSPILERS: Dict[str, Type] = {
    (getattr(cls, "LANGUAGE", name.replace("ReverseFrom", "")).lower()): cls
    for name, cls in inspect.getmembers(reverse_module, inspect.isclass)
    if name.startswith("ReverseFrom")
}

ORIGIN_CHOICES = sorted(REVERSE_TRANSPILERS.keys())

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

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando en el parser.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            CustomArgumentParser: Parser configurado para el subcomando
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
            help=_("Lenguaje de origen del código fuente ({})").format(
                ", ".join(ORIGIN_CHOICES)
            ),
            required=True,
        )
        parser.add_argument(
            "--destino",
            help=_("Lenguaje de destino para la transpilación ({})").format(
                ", ".join(sorted(TRANSPILERS.keys()))
            ),
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
        if _detect_encoding is None:
            logger.debug(
                "chardet no está instalado; se asumirá codificación utf-8 para %s",
                archivo,
            )
            return "utf-8"

        with open(archivo, "rb") as f:
            raw_data = f.read()
        resultado = _detect_encoding(raw_data)
        encoding = resultado.get("encoding") if isinstance(resultado, dict) else None
        if not encoding:
            logger.warning(
                "No se pudo detectar la codificación para %s, usando utf-8", archivo
            )
            encoding = "utf-8"
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
            raise UnsupportedLanguageError(
                f"No hay parser disponible para el lenguaje de origen '{origen}'"
            )
        if destino not in TRANSPILERS:
            raise UnsupportedLanguageError(
                f"No hay transpilador disponible para el lenguaje de destino '{destino}'"
            )

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
            origen = args.origen.lower()
            destino = args.destino.lower()

            logger.debug(f"Iniciando validación del archivo {args.archivo}")

            validar_archivo_existente(args.archivo)

            # Validar archivo
            if error := self._validar_archivo(args.archivo, origen):
                raise CommandError(error)

            # Verificar dependencias
            self._verificar_dependencias(origen, destino)

            # Validar transpiladores
            reverse_cls = REVERSE_TRANSPILERS.get(origen)
            transp_cls = TRANSPILERS.get(destino)

            logger.debug(
                f"Usando transpilador {reverse_cls.__name__} para origen {origen}"
            )
            logger.debug(
                f"Usando transpilador {transp_cls.__name__} para destino {destino}"
            )

            # Detectar codificación y leer archivo
            codificacion = self._detectar_codificacion(args.archivo)
            logger.debug(f"Codificación detectada para {args.archivo}: {codificacion}")

            with archivo_fuente(args.archivo, codificacion) as f:
                contenido = f.read()
                if not contenido.strip():
                    raise ValidationError(f"El archivo '{args.archivo}' está vacío")

            # Transpilar código
            logger.info(f"Iniciando transpilación de {origen} a {destino}")
            ast = reverse_cls().load_file(args.archivo)
            codigo = transp_cls().generate_code(ast)

            mostrar_info(
                _("Código transpilado ({name}):").format(name=transp_cls.__name__)
            )
            print(codigo)
            if destino == "python":
                lineas = codigo.splitlines()
                previsualizacion = [linea.replace("'", "") for linea in lineas]
                if previsualizacion != lineas:
                    print("# Vista previa sin comillas:")
                    print("\n".join(previsualizacion))
            return 0

        except (UnicodeDecodeError, UnicodeError) as exc:
            logger.error(f"Error de codificación: {exc}", exc_info=True)
            mostrar_error(f"Error de codificación al leer '{args.archivo}'")
            return 1
        except OSError as exc:
            if isinstance(exc, FileNotFoundError):
                raise
            logger.error(f"Error de E/S: {exc}", exc_info=True)
            mostrar_error(f"Error al leer el archivo: {exc}")
            return 1
        except NotImplementedError as exc:
            logger.error(f"Funcionalidad no implementada: {exc}", exc_info=True)
            mostrar_error(str(exc))
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
