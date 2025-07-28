import logging
import os
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import patch

from cobra.cli.commands.compile_cmd import TRANSPILERS
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.interpreter import InterpretadorCobra
from core.sandbox import ejecutar_en_sandbox, ejecutar_en_sandbox_js
from cobra.cli.commands.base import BaseCommand
from cobra.cli.i18n import _
from cobra.cli.utils.messages import mostrar_error, mostrar_info


class VerifyCommand(BaseCommand):
    """Verifica que la salida sea la misma en distintos lenguajes."""

    name = "verificar"
    SUPPORTED_LANGUAGES = {"python", "js"}

    def register_subparser(self, subparsers):
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

    def _read_source_file(self, file_path: str) -> str:
        """Lee el contenido del archivo fuente.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Contenido del archivo
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            PermissionError: Si no hay permisos para leer el archivo
            UnicodeDecodeError: Si hay error al decodificar el archivo
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(_("El archivo '{}' no existe").format(file_path))
        except PermissionError:
            raise PermissionError(
                _("No hay permisos para leer el archivo '{}'").format(file_path)
            )
        except UnicodeDecodeError:
            raise UnicodeDecodeError(
                _("Error al decodificar el archivo '{}'").format(file_path)
            )

    def _compile_and_execute(
        self, ast, lang: str, transpiler
    ) -> tuple[Optional[str], Optional[str]]:
        """Compila y ejecuta el código en el lenguaje especificado.
        
        Args:
            ast: AST a compilar
            lang: Lenguaje objetivo
            transpiler: Transpilador a utilizar
            
        Returns:
            Tupla con (salida, error)
        """
        try:
            codigo_gen = transpiler.generate_code(ast)
        except Exception as e:
            logging.error("Error generando código para %s: %s", lang, str(e))
            return None, f"Error al generar código: {str(e)}"

        try:
            if lang == "python":
                salida = ejecutar_en_sandbox(codigo_gen)
            else:
                salida = ejecutar_en_sandbox_js(codigo_gen)
            return salida, None
        except Exception as e:
            logging.error("Error ejecutando código para %s: %s", lang, str(e))
            return None, f"Error al ejecutar: {str(e)}"

    def run(self, args) -> int:
        """Ejecuta la lógica del comando.
        
        Args:
            args: Argumentos del comando
            
        Returns:
            0 si la verificación es exitosa, 1 en caso de error
        """
        try:
            lenguajes = [lang.strip() for lang in args.lenguajes.split(",") if lang.strip()]
            self._validate_languages(lenguajes)
            
            codigo = self._read_source_file(args.archivo)
            
            # Procesar el código fuente
            tokens = Lexer(codigo).tokenizar()
            ast = Parser(tokens).parsear()
            
            # Obtener salida esperada
            with patch("sys.stdout", new_callable=StringIO) as out:
                InterpretadorCobra().ejecutar_ast(ast)
            esperado = out.getvalue()

            # Verificar cada lenguaje
            diferencias: Dict[str, str] = {}
            for lang in lenguajes:
                transpiler = TRANSPILERS[lang]()
                salida, error = self._compile_and_execute(ast, lang, transpiler)
                
                if error:
                    diferencias[lang] = error
                elif salida != esperado:
                    diferencias[lang] = salida

            if diferencias:
                mostrar_error(_("Se encontraron diferencias:"))
                for lang, salida in diferencias.items():
                    mostrar_error(f"{lang}: {salida.strip()}")
                return 1

            mostrar_info(_("Todas las salidas coinciden"))
            return 0
            
        except (ValueError, FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            mostrar_error(str(e))
            return 1
        except Exception as e:
            logging.exception("Error inesperado")
            mostrar_error(f"Error inesperado: {str(e)}")
            return 1