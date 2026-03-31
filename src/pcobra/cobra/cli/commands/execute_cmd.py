import importlib
import logging
import os
import sys
from pathlib import Path
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.utils.validators import (
    normalizar_validadores_extra,
    validar_archivo_existente,
)
from pcobra.cobra.cli.utils.autocomplete import files_completer
from pcobra.cobra.cli.target_policies import (
    DOCKER_EXECUTABLE_TARGETS,
    OFFICIAL_RUNTIME_TARGETS_HELP,
    build_runtime_capability_message,
    parse_runtime_target,
    resolve_docker_backend,
)
from pcobra.cobra.core import Lexer, LexerError
from pcobra.cobra.core import Parser, ParserError
from pcobra.cobra.transpilers import module_map
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.semantic_validators import PrimitivaPeligrosaError, construir_cadena
from pcobra.core.semantic_validators.base import ValidadorBase
from pcobra.core.resource_limits import limitar_cpu_segundos

sys.modules.setdefault("cli.commands.execute_cmd", sys.modules[__name__])


def _importar_modulo_sandbox() -> Any:
    """Resuelve sandbox runtime priorizando namespace canónico."""

    try:
        module = importlib.import_module("pcobra.core.sandbox")
    except ModuleNotFoundError as canon_exc:  # pragma: no cover - fallback legacy
        try:
            module = importlib.import_module("core.sandbox")
        except ModuleNotFoundError:
            raise canon_exc
        _validar_modulo_sandbox_legacy(module)
        logging.getLogger(__name__).warning(
            "Se usó compatibilidad legacy para resolver 'core.sandbox'. "
            "Migre a 'pcobra.core.sandbox'."
        )

    required = (
        "ejecutar_en_sandbox",
        "ejecutar_en_contenedor",
        "SecurityError",
        "validar_dependencias",
    )
    missing = [name for name in required if not hasattr(module, name)]
    if missing:
        raise ImportError(
            f"El módulo '{module.__name__}' no define: {', '.join(missing)}"
        )
    return module


def _validar_modulo_sandbox_legacy(module: Any) -> None:
    """Valida que el fallback legacy apunte al paquete esperado."""

    module_file = getattr(module, "__file__", None)
    if not module_file:
        raise ImportError("El módulo legacy 'core.sandbox' no expone __file__")

    resolved = Path(module_file).resolve().parts
    expected_suffix = ("pcobra", "core", "sandbox.py")
    if tuple(resolved[-len(expected_suffix):]) != expected_suffix:
        raise ImportError(
            "El módulo legacy 'core.sandbox' no apunta al paquete esperado "
            f"('pcobra.core.sandbox'). Ruta detectada: {module_file}"
        )


class _SandboxModuleProxy:
    """Proxy para compatibilidad legacy sin import implícito en carga de módulo."""

    def __getattr__(self, name: str) -> Any:
        return getattr(_importar_modulo_sandbox(), name)


sandbox_module = _SandboxModuleProxy()


def ejecutar_en_sandbox(*args: Any, **kwargs: Any) -> Any:
    return sandbox_module.ejecutar_en_sandbox(*args, **kwargs)


def ejecutar_en_contenedor(*args: Any, **kwargs: Any) -> Any:
    return sandbox_module.ejecutar_en_contenedor(*args, **kwargs)


def validar_dependencias(*args: Any, **kwargs: Any) -> Any:
    return sandbox_module.validar_dependencias(*args, **kwargs)


def _detectar_raiz_proyecto_desde_archivo(archivo: str) -> str:
    """Detecta una raíz de proyecto estable a partir del archivo objetivo."""
    candidato = Path(archivo).resolve()
    if candidato.is_file():
        candidato = candidato.parent
    for ruta in (candidato, *candidato.parents):
        if (ruta / "cobra.toml").exists() or (ruta / "cobra.mod").exists():
            return str(ruta)
    return str(Path(module_map.COBRA_TOML_PATH).resolve().parent)


def _obtener_interpretador_cls():
    """Obtiene la clase de intérprete respetando posibles mocks de pruebas."""

    return getattr(sys.modules[__name__], "InterpretadorCobra", InterpretadorCobra)


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
            "--debug",
            action="store_true",
            default=False,
            help=_("Show debug messages"),
        )
        parser.add_argument(
            "--sandbox",
            action="store_true",
            help=_("Ejecuta el código en una sandbox"),
        )
        parser.add_argument(
            "--contenedor",
            type=lambda value: parse_runtime_target(
                value,
                allowed_targets=DOCKER_EXECUTABLE_TARGETS,
                capability="ejecución en contenedor Docker",
            ),
            choices=DOCKER_EXECUTABLE_TARGETS,
            help=_(
                "Ejecuta el código en un contenedor Docker con runtime oficial "
                "({targets}). Esta opción ejecuta de verdad el programa; no basta con que el target "
                "sea un target oficial de salida. {policy}"
            ).format(
                targets=OFFICIAL_RUNTIME_TARGETS_HELP,
                policy=build_runtime_capability_message(
                    capability="ejecución en contenedor Docker",
                    allowed_targets=DOCKER_EXECUTABLE_TARGETS,
                ),
            ),
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

        debug = bool(getattr(args, "debug", False))
        verbose = int(getattr(args, "verbose", 0) or 0)
        depurar = debug or verbose > 0 or bool(getattr(args, "depurar", False))
        formatear = bool(getattr(args, "formatear", False))
        seguro = getattr(args, "seguro", True)
        raw_extra_validators = getattr(args, "extra_validators", None)
        try:
            extra_validators = normalizar_validadores_extra(raw_extra_validators)
        except TypeError:
            mostrar_error(_("Los validadores extra deben ser una ruta o lista de rutas"))
            return 1
        sandbox = getattr(args, "sandbox", False)
        contenedor = getattr(args, "contenedor", None)
        allow_insecure_fallback = bool(getattr(args, "allow_insecure_fallback", False))

        try:
            raiz_proyecto = _detectar_raiz_proyecto_desde_archivo(args.archivo)
            validar_dependencias(
                "python",
                module_map.get_toml_map(),
                base_dir=raiz_proyecto,
            )
        except (ValueError, FileNotFoundError) as dep_err:
            mostrar_error(f"Error de dependencias: {dep_err}")
            return 1

        if formatear and not self._formatear_codigo(args.archivo):
            return 1

        self.logger.setLevel(logging.DEBUG if depurar else logging.INFO)

        try:
            with open(args.archivo, "r", encoding="utf-8") as f:
                codigo = f.read()
        except (PermissionError, UnicodeDecodeError) as e:
            mostrar_error(f"Error al leer el archivo: {e}")
            return 1

        def ejecutar():
            if sandbox:
                return self._ejecutar_en_sandbox(
                    codigo,
                    seguro,
                    extra_validators,
                    allow_insecure_fallback=allow_insecure_fallback,
                )
            if contenedor:
                return self._ejecutar_en_contenedor(codigo, contenedor)
            return self._ejecutar_normal(codigo, seguro, extra_validators)

        try:
            return self._limitar_recursos(ejecutar)
        except TimeoutError as e:
            mostrar_error(str(e))
            return 1

    def _ejecutar_en_sandbox(
        self,
        codigo: str,
        seguro: bool,
        extra_validators: Any,
        *,
        allow_insecure_fallback: bool = False,
    ) -> int:
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
            salida = sandbox_callable(
                script,
                allow_insecure_fallback=allow_insecure_fallback,
            )
            if salida:
                mostrar_info(str(salida))
            return 0
        except sandbox_module.SecurityError as e:
            self.logger.error("Error de seguridad en sandbox", extra={"error": str(e)})
            mostrar_error(f"Error de seguridad en sandbox: {e}")
            return 1
        except RuntimeError as e:
            self.logger.error("Error de ejecución en sandbox", extra={"error": str(e)})
            mensaje = f"Error de ejecución en sandbox: {e}"
            if "RestrictedPython" in str(e):
                mensaje += (
                    "\nSugerencia: instala RestrictedPython para el modo seguro "
                    "(por ejemplo: pip install RestrictedPython)."
                )
            mostrar_error(mensaje)
            return 1

    def _ejecutar_en_contenedor(self, codigo: str, contenedor: str) -> int:
        """Ejecuta el código en un contenedor Docker."""
        try:
            backend_runtime = resolve_docker_backend(contenedor)
            salida = ejecutar_en_contenedor(codigo, backend_runtime)
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

        interpretador_cls = _obtener_interpretador_cls()
        validadores_normalizados = extra_validators

        if seguro:
            try:
                if extra_validators is None:
                    validadores_normalizados = None
                elif isinstance(extra_validators, str):
                    validadores_normalizados = interpretador_cls._cargar_validadores(extra_validators)
                elif isinstance(extra_validators, list):
                    if all(isinstance(ruta, str) for ruta in extra_validators):
                        acumulado: list[Any] = []
                        for ruta in extra_validators:
                            try:
                                acumulado.extend(interpretador_cls._cargar_validadores(ruta))
                            except Exception as exc:
                                raise ValueError(
                                    _("No se pudieron cargar los validadores extra desde '{path}': {error}").format(
                                        path=ruta,
                                        error=exc,
                                    )
                                ) from exc
                        validadores_normalizados = acumulado
                    else:
                        validadores_normalizados = extra_validators

                if validadores_normalizados is not None:
                    if not isinstance(validadores_normalizados, list) or not all(
                        isinstance(validador, ValidadorBase)
                        for validador in validadores_normalizados
                    ):
                        raise TypeError(
                            _("Los validadores extra deben ser una lista de instancias de validadores")
                        )

                validador = construir_cadena(validadores_normalizados)
                for nodo in ast:
                    nodo.aceptar(validador)
            except (TypeError, ValueError) as e:
                self.logger.error("Error cargando validadores extra", extra={"error": str(e)})
                mostrar_error(str(e))
                return 1
            except PrimitivaPeligrosaError as pe:
                self.logger.error("Primitiva peligrosa detectada", extra={"error": str(pe)})
                mostrar_error(str(pe))
                return 1

        try:
            interpretador_cls(
                safe_mode=seguro,
                extra_validators=validadores_normalizados,
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
