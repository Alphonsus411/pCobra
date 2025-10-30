import importlib
import logging
import os
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.utils.validators import validar_archivo_existente
from pcobra.cobra.cli.utils.autocomplete import files_completer
from pcobra.cobra.core import Lexer, LexerError
from pcobra.cobra.core import Parser, ParserError
from pcobra.cobra.transpilers import module_map
from pcobra.core.interpreter import InterpretadorCobra
try:  # pragma: no cover - compatibilidad con alias legacy
    from core import sandbox as sandbox_module
except ModuleNotFoundError:  # pragma: no cover
    from pcobra.core import sandbox as sandbox_module

ejecutar_en_sandbox = sandbox_module.ejecutar_en_sandbox
ejecutar_en_contenedor = sandbox_module.ejecutar_en_contenedor
SecurityError = sandbox_module.SecurityError
validar_dependencias = sandbox_module.validar_dependencias
from pcobra.core.semantic_validators import PrimitivaPeligrosaError, construir_cadena
from pcobra.core.resource_limits import limitar_cpu_segundos


class ExecuteCommand(BaseCommand):
    """Ejecuta un script Cobra desde un archivo."""

    name = "ejecutar"
    logger = logging.getLogger(__name__)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    EXECUTION_TIMEOUT = 30  # segundos

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(self.name, help=_("Ejecuta un script Cobra"))
        parser.add_argument(
            "archivo", help=_("Ruta al archivo a ejecutar")
        ).completer = files_completer()
        parser.add_argument(
            "--sandbox",
            action="store_true",
            help=_("Ejecuta el código en una sandbox"),
        )
        parser.add_argument(
            "--contenedor",
            choices=["python", "js", "cpp", "rust"],
            help=_("Ejecuta el código en un contenedor Docker"),
        )
        parser.set_defaults(cmd=self)
        return parser

    def _validar_archivo(self, archivo: str) -> None:
        """Valida que el archivo exista y no exceda el tamaño máximo permitido.

        Args:
            archivo: Ruta al archivo a validar

        Raises:
            ValueError: Si el archivo no existe o excede el tamaño máximo
                permitido. Los errores de archivo inexistente se convierten
                en ValueError con un mensaje amigable para la CLI.
        """
        try:
            ruta = validar_archivo_existente(archivo)
        except FileNotFoundError as exc:
            raise ValueError(
                _(
                    "No se encontró el archivo '{path}'. "
                    "Verifica la ruta e inténtalo de nuevo."
                ).format(path=archivo)
            ) from exc
        if ruta.stat().st_size > self.MAX_FILE_SIZE:
            raise ValueError(f"El archivo excede el tamaño máximo permitido ({self.MAX_FILE_SIZE} bytes)")

    def _limitar_recursos(self, funcion):
        """Configura límites de CPU y ejecuta una función."""
        try:
            limitar_cpu_segundos(self.EXECUTION_TIMEOUT)
        except RuntimeError as exc:
            raise TimeoutError(f"No se pudo establecer el límite de CPU: {exc}") from exc
        return funcion()

    def run(self, args: Any) -> int:
        """Ejecuta la lógica del comando.

        Args:
            args: Argumentos parseados del comando

        Returns:
            int: 0 si la ejecución fue exitosa, 1 en caso de error
        """
        try:
            self._validar_archivo(args.archivo)
        except ValueError as e:
            mostrar_error(str(e))
            return 1

        depurar = getattr(args, "depurar", False)
        formatear = getattr(args, "formatear", False)
        seguro = getattr(args, "seguro", True)
        extra_validators = getattr(args, "validadores_extra", None)
        sandbox = getattr(args, "sandbox", False)
        contenedor = getattr(args, "contenedor", None)

        if extra_validators and not isinstance(extra_validators, (str, list)):
            mostrar_error("Los validadores extra deben ser una ruta o lista")
            return 1

        try:
            sandbox_module.validar_dependencias("python", module_map.get_toml_map())
        except (ValueError, FileNotFoundError) as dep_err:
            mostrar_error(f"Error de dependencias: {dep_err}")
            return 1

        if formatear and not self._formatear_codigo(args.archivo):
            return 1

        self.logger.setLevel(logging.DEBUG if depurar else logging.ERROR)

        try:
            with open(args.archivo, "r", encoding="utf-8") as f:
                codigo = f.read()
        except (PermissionError, UnicodeDecodeError) as e:
            mostrar_error(f"Error al leer el archivo: {e}")
            return 1

        def ejecutar():
            if sandbox:
                return self._ejecutar_en_sandbox(codigo, seguro, extra_validators)
            if contenedor:
                return self._ejecutar_en_contenedor(codigo, contenedor)
            return self._ejecutar_normal(codigo, seguro, extra_validators)

        try:
            return self._limitar_recursos(ejecutar)
        except TimeoutError as e:
            mostrar_error(str(e))
            return 1

    def _ejecutar_en_sandbox(self, codigo: str, seguro: bool, extra_validators: Any) -> int:
        """Ejecuta el código en un entorno sandbox."""
        try:
            tokens = Lexer(codigo).tokenizar()
            ast = Parser(tokens).parsear()
        except (LexerError, ParserError) as e:
            self.logger.error("Error de análisis en sandbox", extra={"error": str(e)})
            mostrar_error(f"Error de análisis: {e}")
            return 1

        extra_repr = "None"
        if isinstance(extra_validators, (str, list)):
            extra_repr = repr(extra_validators)

        script = (
            "from pcobra.cobra.core import Lexer, Parser\n"
            "from pcobra.core.interpreter import InterpretadorCobra\n"
            f"_codigo = {codigo!r}\n"
            "_tokens = Lexer(_codigo).tokenizar()\n"
            "_ast = Parser(_tokens).parsear()\n"
            f"_interp = InterpretadorCobra(safe_mode={seguro!r}, extra_validators={extra_repr})\n"
            "_interp.ejecutar_ast(_ast)\n"
        )

        try:
            sandbox_callable = ejecutar_en_sandbox
            try:
                alias_module = importlib.import_module("cobra.cli.commands.execute_cmd")
                sandbox_callable = getattr(alias_module, "ejecutar_en_sandbox", sandbox_callable)
            except ModuleNotFoundError:  # pragma: no cover - alias no disponible
                pass
            salida = sandbox_callable(script)
            if salida:
                mostrar_info(str(salida))
            return 0
        except sandbox_module.SecurityError as e:
            self.logger.error("Error de seguridad en sandbox", extra={"error": str(e)})
            mostrar_error(f"Error de seguridad en sandbox: {e}")
            return 1
        except RuntimeError as e:
            self.logger.error("Error de ejecución en sandbox", extra={"error": str(e)})
            mostrar_error(f"Error de ejecución en sandbox: {e}")
            return 1

    def _ejecutar_en_contenedor(self, codigo: str, contenedor: str) -> int:
        """Ejecuta el código en un contenedor Docker."""
        try:
            salida = ejecutar_en_contenedor(codigo, contenedor)
            if salida:
                mostrar_info(str(salida))
            return 0
        except RuntimeError as e:
            self.logger.error("Error en contenedor Docker", extra={"error": str(e)})
            mostrar_error(f"Error ejecutando en contenedor Docker: {e}")
            return 1

    def _ejecutar_normal(self, codigo: str, seguro: bool, extra_validators: Any) -> int:
        """Ejecuta el código normalmente con el intérprete."""
        try:
            tokens = Lexer(codigo).tokenizar()
            ast = Parser(tokens).parsear()
        except (LexerError, ParserError) as e:
            self.logger.error("Error de análisis", extra={"error": str(e)})
            mostrar_error(f"Error de análisis: {e}")
            return 1

        if seguro:
            try:
                validador = construir_cadena(
                    InterpretadorCobra._cargar_validadores(extra_validators)
                    if isinstance(extra_validators, str)
                    else extra_validators
                )
                for nodo in ast:
                    nodo.aceptar(validador)
            except PrimitivaPeligrosaError as pe:
                self.logger.error("Primitiva peligrosa detectada", extra={"error": str(pe)})
                mostrar_error(str(pe))
                return 1

        try:
            InterpretadorCobra(
                safe_mode=seguro,
                extra_validators=extra_validators,
            ).ejecutar_ast(ast)
            return 0
        except Exception as e:
            self.logger.error("Error de ejecución", extra={"error": str(e)})
            mostrar_error(f"Error ejecutando el script: {e}")
            return 1

    @staticmethod
    def _formatear_codigo(archivo: str) -> bool:
        """Formatea el código usando black.

        Args:
            archivo: Ruta al archivo a formatear

        Returns:
            bool: True si el formateo fue exitoso, False en caso contrario
        """
        try:
            import shutil
            if not shutil.which("black"):
                mostrar_error(_("Herramienta 'black' no encontrada en el PATH"))
                return False

            import subprocess
            resultado = subprocess.run(
                ["black", archivo],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if resultado.returncode != 0:
                mostrar_error(f"Error al formatear: {resultado.stderr}")
                return False
            return True
        except Exception as e:
            mostrar_error(f"Error inesperado al formatear: {e}")
            return False
