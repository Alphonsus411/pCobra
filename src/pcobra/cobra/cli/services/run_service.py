import logging
from pathlib import Path
from typing import Any

from pcobra.cobra.bindings.runtime_manager import RuntimeManager
from pcobra.cobra.cli.execution_pipeline import (
    PipelineInput,
    construir_script_sandbox_canonico,
    ejecutar_pipeline_explicito,
    prevalidar_y_parsear_codigo,
    resolver_interpretador_cls,
)
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.internal_compat.legacy_core_sandbox import (
    LEGACY_SANDBOX_COMPAT_FLAG,
    load_legacy_core_sandbox,
)
from pcobra.cobra.cli.mode_policy import validar_politica_modo
from pcobra.cobra.cli.services.contracts import RunRequest, normalize_run_request
from pcobra.cobra.cli.services.format_service import format_code_with_black
from pcobra.cobra.cli.target_policies import resolve_docker_backend
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.utils.validators import validar_archivo_existente
from pcobra.cobra.core import LexerError, ParserError
from pcobra.cobra.core.runtime import (
    InterpretadorCobra,
    PrimitivaPeligrosaError,
    construir_cadena,
    limitar_cpu_segundos,
)
from pcobra.cobra.transpilers import module_map

try:
    from pcobra.cobra.core import sandbox as sandbox_module
except ModuleNotFoundError as canon_exc:  # pragma: no cover
    sandbox_module = load_legacy_core_sandbox(canonical_error=canon_exc)

RUNTIME_MANAGER = RuntimeManager()


def _importar_modulo_sandbox() -> Any:
    """Compatibilidad para tests/adaptadores legacy; evita import dinámico en run."""
    return sandbox_module


def ejecutar_en_sandbox(*args: Any, **kwargs: Any) -> Any:
    return sandbox_module.ejecutar_en_sandbox(*args, **kwargs)


def ejecutar_en_contenedor(*args: Any, **kwargs: Any) -> Any:
    return sandbox_module.ejecutar_en_contenedor(*args, **kwargs)


def validar_dependencias(*args: Any, **kwargs: Any) -> Any:
    return sandbox_module.validar_dependencias(*args, **kwargs)


def detectar_raiz_proyecto_desde_archivo(archivo: str) -> str:
    candidato = Path(archivo).resolve()
    if candidato.is_file():
        candidato = candidato.parent
    for ruta in (candidato, *candidato.parents):
        if (ruta / "cobra.toml").exists() or (ruta / "cobra.mod").exists():
            return str(ruta)
    return str(Path(module_map.COBRA_TOML_PATH).resolve().parent)


class RunService:
    logger = logging.getLogger(__name__)
    max_file_size = 10 * 1024 * 1024
    execution_timeout = 30

    def run(self, request: RunRequest) -> int:
        request = normalize_run_request(request)
        try:
            validar_politica_modo("ejecutar", request, capability="execute")
        except ValueError as e:
            mostrar_error(str(e), registrar_log=False)
            return 1

        try:
            archivo_resuelto = self.validar_archivo(request.archivo)
        except ValueError as e:
            mostrar_error(str(e), registrar_log=False)
            return 1

        depurar = bool(request.debug) or int(request.verbose or 0) > 0
        depurar = depurar or bool(request.depurar)
        formatear = bool(request.formatear)
        seguro = request.seguro
        sandbox = request.sandbox
        contenedor = request.contenedor
        allow_insecure_fallback = bool(request.allow_insecure_fallback)

        extra_validators = request.extra_validators

        try:
            raiz_proyecto = detectar_raiz_proyecto_desde_archivo(str(archivo_resuelto))
            _abi, contrato, _bridge = RUNTIME_MANAGER.validate_command_runtime(
                "python", command="run", sandbox=sandbox, containerized=False
            )
            validar_dependencias(contrato.language, module_map.get_toml_map(), base_dir=raiz_proyecto)
        except (ValueError, FileNotFoundError) as dep_err:
            mostrar_error(f"Error de dependencias: {dep_err}", registrar_log=False)
            return 1

        if formatear and not format_code_with_black(str(archivo_resuelto)):
            return 1

        self.logger.setLevel(logging.DEBUG if depurar else logging.INFO)

        try:
            codigo = Path(archivo_resuelto).read_text(encoding="utf-8")
        except (PermissionError, UnicodeDecodeError) as e:
            mostrar_error(f"Error al leer el archivo: {e}", registrar_log=False)
            return 1

        def ejecutar() -> int:
            if sandbox:
                return self.ejecutar_en_sandbox(codigo, seguro, extra_validators, allow_insecure_fallback=allow_insecure_fallback)
            if contenedor:
                return self.ejecutar_en_contenedor(codigo, contenedor)
            return self.ejecutar_normal(codigo, seguro, extra_validators)

        try:
            return self.limitar_recursos(ejecutar)
        except TimeoutError as e:
            mostrar_error(str(e), registrar_log=False)
            return 1

    def validar_archivo(self, archivo: str) -> Path:
        try:
            resolved_path = validar_archivo_existente(archivo)
        except FileNotFoundError as error:
            self.logger.debug("Validación de archivo falló: %s", error)
            raise ValueError(
                _("No se encontró el archivo '{path}'. Verifica la ruta e inténtalo de nuevo.").format(path=archivo)
            ) from error
        if resolved_path.stat().st_size > self.max_file_size:
            raise ValueError(f"El archivo excede el tamaño máximo permitido ({self.max_file_size} bytes)")
        return resolved_path

    def limitar_recursos(self, funcion: Any) -> int:
        try:
            limitar_cpu_segundos(self.execution_timeout)
        except RuntimeError as exc:
            raise TimeoutError(f"No se pudo establecer el límite de CPU: {exc}") from exc
        return funcion()

    def ejecutar_en_sandbox(
        self,
        codigo: str,
        seguro: bool,
        extra_validators: Any,
        *,
        allow_insecure_fallback: bool = False,
    ) -> int:
        try:
            interpretador_cls = resolver_interpretador_cls(
                module_name=__name__,
                default_cls=InterpretadorCobra,
            )
            setup, _ = ejecutar_pipeline_explicito(
                PipelineInput(
                    codigo="",
                    interpretador_cls=interpretador_cls,
                    safe_mode=seguro,
                    extra_validators=extra_validators,
                ),
                analizar_codigo_fn=lambda _codigo: [],
            )
            prevalidar_y_parsear_codigo(codigo)
        except (LexerError, ParserError) as e:
            mostrar_error(f"Error de análisis: {e}", registrar_log=False)
            return 1
        except (TypeError, ValueError, PrimitivaPeligrosaError) as e:
            mostrar_error(str(e), registrar_log=False)
            return 1

        script = construir_script_sandbox_canonico(
            codigo,
            safe_mode=setup.safe_mode,
            extra_validators=setup.validadores_extra,
        )

        try:
            salida = ejecutar_en_sandbox(script, allow_insecure_fallback=allow_insecure_fallback)
            if salida:
                mostrar_info(str(salida))
            return 0
        except sandbox_module.SecurityError as e:
            mostrar_error(f"Error de seguridad en sandbox: {e}", registrar_log=False)
            return 1
        except RuntimeError as e:
            mensaje = f"Error de ejecución en sandbox: {e}"
            if "RestrictedPython" in str(e):
                mensaje += "\nSugerencia: instala RestrictedPython para el modo seguro (por ejemplo: pip install RestrictedPython)."
            mostrar_error(mensaje, registrar_log=False)
            return 1

    def ejecutar_en_contenedor(self, codigo: str, contenedor: str) -> int:
        try:
            RUNTIME_MANAGER.validate_command_runtime(
                contenedor,
                command="run",
                sandbox=False,
                containerized=True,
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

    def ejecutar_normal(self, codigo: str, seguro: bool, extra_validators: Any) -> int:
        try:
            ejecutar_pipeline_explicito(
                PipelineInput(
                    codigo=codigo,
                    interpretador_cls=resolver_interpretador_cls(module_name=__name__, default_cls=InterpretadorCobra),
                    safe_mode=seguro,
                    extra_validators=extra_validators,
                ),
                construir_cadena_fn=construir_cadena,
                analizar_codigo_fn=prevalidar_y_parsear_codigo,
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
