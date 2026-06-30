import logging
from argparse import ArgumentTypeError
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
from pcobra.cobra.cli.mode_policy import validar_politica_modo
from pcobra.cobra.cli.services.contracts import RunRequest, normalize_run_request
from pcobra.cobra.cli.services.format_service import format_code_with_black
from pcobra.cobra.cli.target_policies import resolve_docker_backend
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.utils.source import read_cobra_source
from pcobra.cobra.cli.utils.validators import validar_archivo_existente
from pcobra.cobra.packaging import es_paquete_cobra
from pcobra.cobra.core import LexerError, ParserError
from pcobra.cobra.core.runtime import (
    InterpretadorCobra,
    PrimitivaPeligrosaError,
    construir_cadena,
    limitar_cpu_segundos,
)
from pcobra.cobra.core.sandbox import ejecutar_en_contenedor as ejecutar_en_contenedor_docker
from pcobra.cobra.transpilers import module_map

from pcobra.cobra.core import sandbox as sandbox_module

RUNTIME_MANAGER = RuntimeManager()


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
            sandbox_module.validar_dependencias(contrato.language, module_map.get_toml_map(), base_dir=raiz_proyecto)
        except (ValueError, FileNotFoundError) as dep_err:
            mostrar_error(f"Error de dependencias: {dep_err}", registrar_log=False)
            return 1

        if formatear and not format_code_with_black(str(archivo_resuelto)):
            return 1

        self.logger.setLevel(logging.DEBUG if depurar else logging.INFO)

        try:
            codigo = read_cobra_source(archivo_resuelto)
        except (PermissionError, UnicodeDecodeError) as e:
            mostrar_error(f"Error al leer el archivo: {e}", registrar_log=False)
            return 1

        def ejecutar() -> int:
            if sandbox:
                return sandbox_module.ejecutar_en_sandbox(
                    codigo,
                    seguro,
                    extra_validators,
                    main_file=archivo_resuelto,
                    allow_insecure_fallback=allow_insecure_fallback,
                )
            if contenedor:
                return self.ejecutar_en_contenedor(codigo, contenedor)
            return self.ejecutar_normal(
                codigo, seguro, extra_validators, main_file=archivo_resuelto
            )

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
        if es_paquete_cobra(resolved_path):
            raise ValueError(
                "El archivo es un paquete Cobra .co, no una fuente ejecutable. "
                "Instálalo o extráelo con el comando paquete antes de ejecutar."
            )
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
        main_file: Path | None = None,
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
                    main_file=main_file,
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
            main_file=main_file,
        )

        try:
            salida = sandbox_module.ejecutar_en_sandbox(script, allow_insecure_fallback=allow_insecure_fallback)
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

    def ejecutar_en_contenedor(self, codigo: str, backend: str) -> int:
        try:
            salida = ejecutar_en_contenedor_docker(
                codigo,
                resolve_docker_backend(backend),
                timeout=self.execution_timeout,
            )
            if salida:
                mostrar_info(str(salida))
            return 0
        except (ArgumentTypeError, RuntimeError, ValueError) as e:
            mostrar_error(f"Error de ejecución en contenedor: {e}", registrar_log=False)
            return 1

    def ejecutar_normal(
        self,
        codigo: str,
        seguro: bool,
        extra_validators: Any,
        *,
        main_file: Path | None = None,
    ) -> int:
        try:
            ejecutar_pipeline_explicito(
                PipelineInput(
                    codigo=codigo,
                    interpretador_cls=resolver_interpretador_cls(module_name=__name__, default_cls=InterpretadorCobra),
                    safe_mode=seguro,
                    extra_validators=extra_validators,
                    main_file=main_file,
                ),
                construir_cadena_fn=construir_cadena,
                analizar_codigo_fn=prevalidar_y_parsear_codigo,
            )
            return 0
        except (LexerError, ParserError) as e:
            mostrar_error(f"Error de análisis: {e}", registrar_log=False)
            return 1
        except (TypeError, ValueError, PermissionError, NameError) as e:
            mostrar_error(str(e), registrar_log=False)
            return 1
        except PrimitivaPeligrosaError as pe:
            mostrar_error(str(pe), registrar_log=False)
            return 1
        except Exception as e:
            mostrar_error(f"Error ejecutando el script: {e}", registrar_log=False)
            return 1
