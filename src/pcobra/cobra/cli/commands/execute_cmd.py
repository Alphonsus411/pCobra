import importlib
import logging
import sys
from pathlib import Path
from typing import Any

from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.mode_policy import validar_politica_modo
from pcobra.cobra.cli.services.format_service import format_code_with_black
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.utils.validators import (
    normalizar_validadores_extra,
    validar_archivo_existente,
)
from pcobra.cobra.cli.utils.autocomplete import files_completer
from pcobra.cobra.bindings.runtime_manager import RuntimeManager
from pcobra.cobra.cli.target_policies import (
    DOCKER_EXECUTABLE_TARGETS,
    OFFICIAL_RUNTIME_TARGETS_HELP,
    build_runtime_capability_message,
    parse_runtime_target,
    resolve_docker_backend,
)
from pcobra.cobra.core import LexerError
from pcobra.cobra.core import ParserError
from pcobra.cobra.cli.execution_pipeline import (
    analizar_codigo,
    construir_script_sandbox_canonico,
    ejecutar_pipeline_explicito,
    PipelineInput,
    resolver_interpretador_cls,
)
from pcobra.cobra.transpilers import module_map
from pcobra.cobra.core.runtime import (
    InterpretadorCobra,
    PrimitivaPeligrosaError,
    construir_cadena,
    limitar_cpu_segundos,
)

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
RUNTIME_MANAGER = RuntimeManager()


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


class ExecuteCommand(BaseCommand):
    """Ejecuta un script Cobra desde un archivo."""

    name = "ejecutar"
    capability = "execute"
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

    def _validar_archivo(self, archivo: str) -> Path:
        """Valida que el archivo exista y no exceda el tamaño máximo permitido.

        Args:
            archivo: Ruta al archivo a validar

        Returns:
            Path: Ruta normalizada y resuelta del archivo.

        Raises:
            ValueError: Si el archivo no existe o excede el tamaño máximo
                permitido. Los errores de archivo inexistente se convierten
                en ValueError con un mensaje amigable para la CLI.
        """
        try:
            resolved_path = validar_archivo_existente(archivo)
        except FileNotFoundError as error:
            self.logger.debug("Validación de archivo falló: %s", error)
            raise ValueError(
                _(
                    "No se encontró el archivo '{path}'. "
                    "Verifica la ruta e inténtalo de nuevo."
                ).format(path=archivo)
            ) from error
        if resolved_path.stat().st_size > self.MAX_FILE_SIZE:
            raise ValueError(f"El archivo excede el tamaño máximo permitido ({self.MAX_FILE_SIZE} bytes)")
        return resolved_path

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
            validar_politica_modo(self.name, args, capability=self.capability)
        except ValueError as e:
            mostrar_error(str(e), registrar_log=False)
            return 1

        try:
            archivo_original = args.archivo
            archivo_resuelto = self._validar_archivo(archivo_original)
        except ValueError as e:
            mostrar_error(str(e), registrar_log=False)
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
            mostrar_error(
                _("Los validadores extra deben ser una ruta o lista de rutas"),
                registrar_log=False,
            )
            return 1
        sandbox = getattr(args, "sandbox", False)
        contenedor = getattr(args, "contenedor", None)
        allow_insecure_fallback = bool(getattr(args, "allow_insecure_fallback", False))

        try:
            raiz_proyecto = _detectar_raiz_proyecto_desde_archivo(str(archivo_resuelto))
            _abi_python, contrato_python, _bridge_python = RUNTIME_MANAGER.validate_command_runtime(
                "python",
                command="run",
                sandbox=sandbox,
                containerized=False,
            )
            validar_dependencias(
                contrato_python.language,
                module_map.get_toml_map(),
                base_dir=raiz_proyecto,
            )
        except (ValueError, FileNotFoundError) as dep_err:
            mostrar_error(f"Error de dependencias: {dep_err}", registrar_log=False)
            return 1

        if formatear and not format_code_with_black(str(archivo_resuelto)):
            return 1

        self.logger.setLevel(logging.DEBUG if depurar else logging.INFO)

        try:
            with open(archivo_resuelto, "r", encoding="utf-8") as f:
                codigo = f.read()
        except (PermissionError, UnicodeDecodeError) as e:
            mostrar_error(f"Error al leer el archivo: {e}", registrar_log=False)
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
            mostrar_error(str(e), registrar_log=False)
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
            self._analizar_codigo(codigo)
        except (LexerError, ParserError) as e:
            mostrar_error(f"Error de análisis: {e}", registrar_log=False)
            return 1

        script = construir_script_sandbox_canonico(
            codigo,
            safe_mode=seguro,
            extra_validators=extra_validators,
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
            mostrar_error(f"Error de seguridad en sandbox: {e}", registrar_log=False)
            return 1
        except RuntimeError as e:
            mensaje = f"Error de ejecución en sandbox: {e}"
            if "RestrictedPython" in str(e):
                mensaje += (
                    "\nSugerencia: instala RestrictedPython para el modo seguro "
                    "(por ejemplo: pip install RestrictedPython)."
                )
            mostrar_error(mensaje, registrar_log=False)
            return 1

    def _ejecutar_en_contenedor(self, codigo: str, contenedor: str) -> int:
        """Ejecuta el código en un contenedor Docker."""
        try:
            abi_version, contrato, bridge = RUNTIME_MANAGER.validate_command_runtime(
                contenedor,
                command="run",
                sandbox=False,
                containerized=True,
            )
            self.logger.debug(
                "Ruta de bindings para contenedor '%s': %s (%s) bridge=%s abi=%s",
                contenedor,
                contrato.route.value,
                contrato.execution_boundary,
                bridge.implementation,
                abi_version,
            )

            backend_runtime = resolve_docker_backend(contenedor)
            salida = ejecutar_en_contenedor(codigo, backend_runtime)
            if salida:
                mostrar_info(str(salida))
            return 0
        except ValueError as e:
            mostrar_error(str(e), registrar_log=False)
            return 1
        except RuntimeError as e:
            mostrar_error(f"Error ejecutando en contenedor Docker: {e}", registrar_log=False)
            return 1

    def _ejecutar_normal(self, codigo: str, seguro: bool, extra_validators: Any) -> int:
        """Ejecuta el código normalmente con el intérprete."""
        try:
            ejecutar_pipeline_explicito(
                PipelineInput(
                    codigo=codigo,
                    interpretador_cls=resolver_interpretador_cls(
                        module_name=__name__,
                        default_cls=InterpretadorCobra,
                    ),
                    safe_mode=seguro,
                    extra_validators=extra_validators,
                ),
                construir_cadena_fn=construir_cadena,
                analizar_codigo_fn=analizar_codigo,
            )
            return 0
        except (LexerError, ParserError) as e:
            mostrar_error(f"Error de análisis: {e}", registrar_log=False)
            return 1
        except (TypeError, ValueError) as e:
            mostrar_error(str(e), registrar_log=False)
            return 1
        except PrimitivaPeligrosaError as pe:
            mostrar_error(str(pe), registrar_log=False)
            return 1
        except Exception as e:
            mostrar_error(f"Error ejecutando el script: {e}", registrar_log=False)
            return 1

    def _analizar_codigo(self, codigo: str) -> Any:
        """Pipeline canónico: Lexer(codigo).tokenizar() + Parser(tokens).parsear()."""

        return analizar_codigo(codigo)
