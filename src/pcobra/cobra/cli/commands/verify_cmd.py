import concurrent.futures
import logging
import os
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import patch
from argparse import ArgumentParser

from pcobra.cobra.cli.commands.compile_cmd import TRANSPILERS
from pcobra.cobra.core import Lexer
from pcobra.cobra.core import Parser
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.sandbox import ejecutar_en_sandbox, ejecutar_en_sandbox_js
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.utils.validators import validar_archivo_existente

# Constantes
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
VALID_EXTENSIONS = {'.cobra', '.cbr'}

class VerifyCommand(BaseCommand):
    """Verifica que la salida sea la misma en distintos lenguajes."""

    name = "verificar"
    SUPPORTED_LANGUAGES = {"python", "js"}
    
    def __init__(self) -> None:
        """Inicializa el comando y el intérprete."""
        super().__init__()
        self._interprete = InterpretadorCobra()
        self._logger = logging.getLogger(__name__)

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            El parser configurado para el subcomando
        """
        parser = subparsers.add_parser(
            self.name,
            help=_("Comprueba la salida en varios lenguajes"),
        )
        parser.add_argument(
            "archivo",
            help=_("Archivo de código fuente a verificar")
        )
        parser.add_argument(
            "--lenguajes",
            "-l",
            required=True,
            help=_("Lista de lenguajes separados por comas (soportados: python, js)"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def _validate_languages(self, languages: List[str]) -> None:
        """Valida la lista de lenguajes proporcionada.
        
        Args:
            languages: Lista de lenguajes a validar
            
        Raises:
            ValueError: Si la lista está vacía o contiene lenguajes no soportados
        """
        if not languages:
            raise ValueError(_("La lista de lenguajes no puede estar vacía"))
        
        unsupported = set(languages) - self.SUPPORTED_LANGUAGES
        if unsupported:
            raise ValueError(
                _("Lenguajes no soportados: {}").format(", ".join(unsupported))
            )

    def _validate_file(self, file_path: str) -> None:
        """Valida el archivo de entrada.
        
        Args:
            file_path: Ruta al archivo
            
        Raises:
            ValueError: Si el archivo no es válido
        """
        path = Path(file_path)
        if not path.suffix in VALID_EXTENSIONS:
            raise ValueError(_("Extensión de archivo no válida. Debe ser: {}").format(
                ", ".join(VALID_EXTENSIONS)
            ))
        
        if path.stat().st_size > MAX_FILE_SIZE:
            raise ValueError(_("El archivo es demasiado grande (máximo {} MB)").format(
                MAX_FILE_SIZE // (1024 * 1024)
            ))

    def _read_source_file(self, file_path: str) -> str:
        """Lee el contenido del archivo fuente.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Contenido del archivo
            
        Raises:
            ValueError: Si el archivo no es válido
            FileNotFoundError: Si el archivo no existe
            PermissionError: Si no hay permisos para leer el archivo
        """
        validar_archivo_existente(file_path)
        self._validate_file(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except PermissionError:
            raise PermissionError(
                _("No hay permisos para leer el archivo '{}'").format(file_path)
            )
        except UnicodeDecodeError as e:
            self._logger.error("Error decodificando archivo: %s", str(e))
            raise ValueError(_("Error al decodificar el archivo '{}'").format(file_path))

    def _compile_and_execute(
        self, 
        ast: Any, 
        lang: str, 
        transpiler: Any
    ) -> Tuple[Optional[str], Optional[str]]:
        """Compila y ejecuta el código en el lenguaje especificado.
        
        Args:
            ast: AST a compilar
            lang: Lenguaje objetivo
            transpiler: Transpilador a utilizar
            
        Returns:
            Tupla con (salida, error)
        """
        try:
            if lang not in TRANSPILERS:
                return None, _("Transpilador no encontrado para {}").format(lang)
                
            codigo_gen = transpiler.generate_code(ast)
            
            if lang == "python":
                salida = ejecutar_en_sandbox(codigo_gen)
            else:
                salida = ejecutar_en_sandbox_js(codigo_gen)
                
            # Normalizar terminaciones de línea
            return salida.replace('\r\n', '\n'), None
            
        except Exception as e:
            self._logger.error("Error en %s: %s", lang, str(e))
            return None, str(e)

    def _verify_language(
        self, 
        lang: str, 
        ast: Any, 
        esperado: str
    ) -> Tuple[str, Optional[str]]:
        """Verifica un lenguaje específico.
        
        Args:
            lang: Lenguaje a verificar
            ast: AST del código
            esperado: Salida esperada
            
        Returns:
            Tupla con (lenguaje, error si existe)
        """
        transpiler = TRANSPILERS[lang]()
        salida, error = self._compile_and_execute(ast, lang, transpiler)
        
        if error:
            return lang, error
        elif salida != esperado:
            return lang, salida
            
        return lang, None

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos del comando
            
        Returns:
            0 si la verificación es exitosa, 1 en caso de error
        """
        try:
            if not args.archivo or not args.lenguajes:
                raise ValueError(_("Se requieren archivo y lenguajes"))
                
            lenguajes = [lang.strip() for lang in args.lenguajes.split(",") if lang.strip()]
            self._validate_languages(lenguajes)
            
            codigo = self._read_source_file(args.archivo)
            
            # Procesar el código fuente
            tokens = Lexer(codigo).tokenizar()
            ast = Parser(tokens).parsear()
            
            # Obtener salida esperada
            with patch("sys.stdout", new_callable=StringIO) as out:
                self._interprete.ejecutar_ast(ast)
            esperado = out.getvalue().replace('\r\n', '\n')

            # Verificar lenguajes en paralelo
            diferencias: Dict[str, str] = {}
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futuros = {
                    executor.submit(self._verify_language, lang, ast, esperado): lang 
                    for lang in lenguajes
                }
                
                for futuro in concurrent.futures.as_completed(futuros):
                    lang, error = futuro.result()
                    if error:
                        diferencias[lang] = error

            if diferencias:
                mostrar_error(_("Se encontraron diferencias:"))
                for lang, salida in diferencias.items():
                    mostrar_error(f"{lang}: {salida.strip()}")
                return 1

            mostrar_info(_("Todas las salidas coinciden"))
            return 0
            
        except (ValueError, PermissionError) as e:
            mostrar_error(str(e))
            return 1
        except Exception as e:
            self._logger.exception("Error inesperado")
            mostrar_error(f"Error inesperado: {str(e)}")
            return 1