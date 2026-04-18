import logging
import multiprocessing
import os
import inspect
from argparse import ArgumentTypeError
from importlib import import_module
from importlib.metadata import entry_points

from pcobra.cobra.build import backend_pipeline
from pcobra.cobra.cli.target_policies import (
    OFFICIAL_TRANSPILATION_TARGETS,
    parse_target,
    parse_target_list,
)
from pcobra.cobra.imports._module_map_api import get_toml_map
from pcobra.core.ast_cache import obtener_ast
from pcobra.core.sandbox import validar_dependencias
from pcobra.core.semantic_validators import (
    PrimitivaPeligrosaError,
    construir_cadena,
)
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.mode_policy import validar_politica_modo
from pcobra.cobra.cli.deprecation_policy import (
    enforce_target_deprecation_policy,
    visible_public_targets,
)
from pcobra.cobra.cli.internal_compat.legacy_targets import enabled_internal_legacy_targets
from pcobra.cobra.cli.internal_compat.legacy_flags import add_internal_legacy_targets_flag
from pcobra.cobra.cli.utils.messages import mostrar_advertencia, mostrar_error, mostrar_info
from pcobra.cobra.cli.utils.validators import validar_archivo_existente
from pcobra.cobra.cli.utils.autocomplete import files_completer
from pcobra.cobra.core import ParserError
from pcobra.core.cobra_config import tiempo_max_transpilacion

# Constantes de configuración
MAX_PROCESSES = 4
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
PROCESS_TIMEOUT = tiempo_max_transpilacion()
MAX_LANGUAGES = 10

_PLUGIN_TRANSPILERS: dict[str, type] = {}
_ENTRYPOINTS_LOADED = False


def register_transpiler_backend(backend: str, transpiler_cls, *, context: str) -> str:
    """Registra un backend externo solo si usa nombre canónico oficial exacto."""
    canonical = _validate_official_backend_or_raise(backend, context=context)
    raw_normalized = backend.strip().lower()
    if raw_normalized not in OFFICIAL_TRANSPILATION_TARGETS:
        raise ValueError(
            _(
                "Backend no permitido en {context}: {backend}. "
                "Los plugins/transpiladores externos solo pueden registrar targets oficiales canónicos: {supported}"
            ).format(
                context=context,
                backend=backend,
                supported=", ".join(OFFICIAL_TRANSPILATION_TARGETS),
            )
        )
    _validate_transpiler_class_or_raise(
        transpiler_cls,
        backend=canonical,
        context=context,
    )
    _PLUGIN_TRANSPILERS[canonical] = transpiler_cls
    return canonical


def _validate_transpiler_class_or_raise(transpiler_cls, *, backend: str, context: str) -> None:
    """Valida el contrato mínimo de un transpilador externo antes de registrarlo."""
    if not isinstance(transpiler_cls, type):
        raise ValueError(
            _(
                "Contrato inválido para backend '{backend}' en {context}: "
                "se esperaba una clase, recibido {type_name}."
            ).format(
                backend=backend,
                context=context,
                type_name=type(transpiler_cls).__name__,
            )
        )

    if not callable(transpiler_cls):
        raise ValueError(
            _(
                "Contrato inválido para backend '{backend}' en {context}: "
                "la clase '{class_name}' no es callable."
            ).format(
                backend=backend,
                context=context,
                class_name=transpiler_cls.__name__,
            )
        )

    generate_code = getattr(transpiler_cls, "generate_code", None)
    if not callable(generate_code):
        raise ValueError(
            _(
                "Contrato inválido para backend '{backend}' en {context}: "
                "la clase '{class_name}' no implementa el método callable 'generate_code'."
            ).format(
                backend=backend,
                context=context,
                class_name=transpiler_cls.__name__,
            )
        )

    try:
        signature = inspect.signature(transpiler_cls)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            _(
                "Contrato inválido para backend '{backend}' en {context}: "
                "no se pudo inspeccionar la firma de '{class_name}': {cause}"
            ).format(
                backend=backend,
                context=context,
                class_name=transpiler_cls.__name__,
                cause=exc,
            )
        ) from exc

    required_params = [
        p.name
        for p in signature.parameters.values()
        if p.default is inspect.Signature.empty
        and p.kind
        in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
    ]
    if required_params:
        raise ValueError(
            _(
                "Contrato inválido para backend '{backend}' en {context}: "
                "la clase '{class_name}' requiere argumentos de inicialización "
                "({params}). El protocolo soportado por plugins exige constructor sin argumentos."
            ).format(
                backend=backend,
                context=context,
                class_name=transpiler_cls.__name__,
                params=", ".join(required_params),
            )
        )


def _validate_official_backend_or_raise(backend: str, *, context: str) -> str:
    """Validador único de backend oficial conectado a la matriz canónica."""
    try:
        return parse_target(backend)
    except ArgumentTypeError as exc:
        raise ValueError(str(exc)) from exc


def _validate_entrypoint_backend_or_raise(backend: str, *, context: str) -> str:
    """Acepta únicamente nombres canónicos oficiales en entry points."""
    normalized = _validate_official_backend_or_raise(backend, context=context)
    raw_normalized = backend.strip().lower()
    if raw_normalized != normalized:
        raise ValueError(
            _(
                "Backend no permitido en {context}: {backend}. "
                "Los entry points solo pueden usar nombres canónicos oficiales: {supported}"
            ).format(
                context=context,
                backend=backend,
                supported=", ".join(OFFICIAL_TRANSPILATION_TARGETS),
            )
        )
    return normalized


def _iter_transpiler_entry_points():
    try:
        return entry_points(group="cobra.transpilers")
    except TypeError:  # Compatibilidad con versiones antiguas
        return entry_points().get("cobra.transpilers", [])



def load_entrypoint_transpilers() -> tuple[int, int, int]:
    """Carga entry points de transpiladores sin permitir aliases o targets no oficiales."""
    loaded = 0
    rejected = 0
    skipped_existing = 0
    entrypoint_items = list(_iter_transpiler_entry_points())
    logging.info(
        "Iniciando carga de plugins de transpiladores por entry points: total=%d",
        len(entrypoint_items),
    )

    for ep in entrypoint_items:
        try:
            normalized_ep_name = _validate_entrypoint_backend_or_raise(
                ep.name,
                context="plugins(entry_points)",
            )
            module_name, class_name = ep.value.split(":", 1)
            if not all(c.isalnum() or c in "._" for c in module_name + class_name):
                raise ValueError(f"Nombre de módulo o clase inválido: {ep.value}")
                continue
            cls = getattr(import_module(module_name), class_name)
            if normalized_ep_name in _PLUGIN_TRANSPILERS:
                logging.warning(
                    "Plugin de transpilador '%s' omitido: '%s' ya existe en el registro canónico",
                    ep.name,
                    normalized_ep_name,
                )
                skipped_existing += 1
                continue
            register_transpiler_backend(normalized_ep_name, cls, context="plugins(entry_points)")
            loaded += 1
        except ValueError as exc:
            rejected += 1
            logging.error(
                "Plugin de transpilador '%s' rechazado por política/contrato: %s",
                ep.name,
                exc,
            )
        except Exception as exc:
            rejected += 1
            logging.error("Error cargando transpilador '%s': %s", ep.name, exc)

    logging.info(
        (
            "Carga de plugins de transpiladores finalizada: "
            "total=%d cargados=%d rechazados=%d omitidos=%d"
        ),
        len(entrypoint_items),
        loaded,
        rejected,
        skipped_existing,
    )
    return loaded, rejected, skipped_existing


def _ensure_entrypoints_loaded_once() -> None:
    """Asegura la carga idempotente de entry points de transpiladores."""
    global _ENTRYPOINTS_LOADED
    if _ENTRYPOINTS_LOADED:
        logging.debug("Carga de plugins por entry points omitida: ya fue ejecutada.")
        return

    load_entrypoint_transpilers()
    _ENTRYPOINTS_LOADED = True

TARGETS_HELP = ", ".join(visible_public_targets(OFFICIAL_TRANSPILATION_TARGETS))


def parse_official_target_list(value: str) -> list[str]:
    """Normaliza una lista de targets usando el validador canónico único."""
    return parse_target_list(value)

def validate_file(filepath: str) -> bool:
    """Valida que el archivo sea accesible y cumpla con los límites establecidos."""
    try:
        path = validar_archivo_existente(filepath)
    except FileNotFoundError:
        raise ValueError(f"'{filepath}' no es un archivo válido")
    if not os.access(path, os.R_OK):
        raise ValueError(f"No hay permisos de lectura para '{filepath}'")
    if os.path.getsize(path) > MAX_FILE_SIZE:
        raise ValueError(f"El archivo excede el tamaño máximo permitido ({MAX_FILE_SIZE} bytes)")
    return True

def validar_dependencias_con_alias(backend: str, mod_info: dict) -> None:
    """Valida dependencias usando únicamente el target canónico público."""
    validar_dependencias(backend, mod_info)


def _target_label(target: str) -> str:
    return target.replace("_", " ").capitalize()


def _transpile_with_pipeline_or_plugin(ast, lang: str) -> str:
    plugin_cls = _PLUGIN_TRANSPILERS.get(lang)
    if plugin_cls is not None:
        return plugin_cls().generate_code(ast)
    return backend_pipeline.transpile(ast, lang)


def run_transpiler_pool(languages: list, ast, executor) -> list:
    """Ejecuta los transpiladores en paralelo con límites de seguridad."""
    if len(languages) > MAX_LANGUAGES:
        raise ValueError(_("Demasiados lenguajes especificados"))
    with multiprocessing.Pool(processes=min(len(languages), MAX_PROCESSES)) as pool:
        # ``map_async`` no acepta ``timeout`` como argumento, por lo que el límite
        # de ejecución se controla exclusivamente mediante ``AsyncResult.get``.
        return pool.map_async(
            executor,
            [(lang, ast) for lang in languages],
        ).get(timeout=PROCESS_TIMEOUT)

class CompileCommand(BaseCommand):
    """Transpila un archivo Cobra a distintos lenguajes."""

    name = "compilar"
    capability = "codegen"
    aliases = ("transpilar",)
    requires_sqlite_key: bool = True

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        lang_choices = list(OFFICIAL_TRANSPILATION_TARGETS) + list(enabled_internal_legacy_targets())
        parser = subparsers.add_parser(
            self.name,
            help=_("Transpila un archivo"),
            aliases=list(self.aliases),
        )
        parser.add_argument("archivo").completer = files_completer()
        parser.add_argument(
            "--tipo",
            type=parse_target,
            choices=lang_choices,
            default="python",
            help=_("Tipo de código generado ({targets}).").format(targets=TARGETS_HELP),
        )
        parser.add_argument(
            "--backend",
            type=parse_target,
            choices=lang_choices,
            help=_("Alias deprecado de --tipo ({targets}).").format(targets=TARGETS_HELP),
        )
        parser.add_argument(
            "--tipos",
            type=parse_official_target_list,
            help=_("Lista de lenguajes separados por comas ({targets}).").format(targets=TARGETS_HELP),
        )
        add_internal_legacy_targets_flag(parser)
        parser.set_defaults(cmd=self)
        return parser

    def _ejecutar_transpilador(self, parametros: tuple) -> tuple:
        """Ejecuta un transpilador específico."""
        lang, ast = parametros
        code = _transpile_with_pipeline_or_plugin(ast, lang)
        return lang, code

    def run(self, args):
        """Ejecuta la lógica del comando."""
        archivo = args.archivo

        try:
            validar_politica_modo(self.name, args, capability=self.capability)
        except ValueError as e:
            mostrar_error(str(e))
            return 1

        try:
            validate_file(archivo)
        except ValueError as e:
            mostrar_error(str(e))
            return 1

        _ensure_entrypoints_loaded_once()

        tipos_argument = getattr(args, "tipos", None)
        if isinstance(tipos_argument, str):
            try:
                tipos_argument = parse_official_target_list(tipos_argument)
            except ArgumentTypeError as parse_error:
                mostrar_error(str(parse_error))
                return 1

        mod_info = get_toml_map()
        preferred_backend = getattr(args, "backend", None) or getattr(args, "tipo", None)
        if getattr(args, "backend", None):
            mostrar_advertencia(
                _("La opción --backend está deprecada en 'compilar'; use --tipo. Se eliminará en una versión futura.")
            )
        try:
            resolution, _runtime = backend_pipeline.resolve_backend_runtime(
                archivo,
                {"preferred_backend": preferred_backend},
            )
            transpilador_objetivo = _validate_official_backend_or_raise(
                resolution.backend,
                context="CLI",
            )
            enforce_target_deprecation_policy(
                command=self.name,
                target=transpilador_objetivo,
                args=args,
            )
        except ValueError as validation_err:
            mostrar_error(str(validation_err))
            return 1

        try:
            if tipos_argument:
                langs = list(tipos_argument)
                for lang in langs:
                    enforce_target_deprecation_policy(
                        command=self.name,
                        target=lang,
                        args=args,
                    )
                    validar_dependencias_con_alias(lang, mod_info)
            else:
                validar_dependencias_con_alias(transpilador_objetivo, mod_info)
        except (ValueError, FileNotFoundError) as dep_err:
            mostrar_error(f"Error de dependencias: {dep_err}")
            return 1

        try:
            with open(archivo, "r", encoding="utf-8") as f:
                codigo = f.read()

            ast = obtener_ast(codigo)
            validador = construir_cadena()
            for nodo in ast:
                nodo.aceptar(validador)

            if tipos_argument:
                lenguajes = list(tipos_argument)
                for lang in lenguajes:
                    try:
                        _validate_official_backend_or_raise(lang, context="CLI --tipos")
                    except ValueError as validation_err:
                        raise ValueError(str(validation_err))
                    try:
                        backend_pipeline.resolve_backend_runtime(
                            archivo,
                            {"preferred_backend": lang},
                        )
                    except ValueError as validation_err:
                        raise ValueError(str(validation_err))
                
                try:
                    resultados = run_transpiler_pool(lenguajes, ast, self._ejecutar_transpilador)
                    for lang, resultado in resultados:
                        mostrar_info(
                            _("Código generado para {lang}:").format(
                                lang=f"{_target_label(lang)} ({lang})",
                            )
                        )
                        print(resultado)
                except multiprocessing.TimeoutError:
                    mostrar_error(_("Tiempo de ejecución excedido"))
                    return 1
            else:
                transpilador = transpilador_objetivo
                resultado = _transpile_with_pipeline_or_plugin(ast, transpilador)
                mostrar_info(
                    _("Código generado:")
                )
                print(resultado)
            return 0

        except PrimitivaPeligrosaError as pe:
            mostrar_error(str(pe))
            return 1
        except ParserError as se:
            mostrar_error(f"Error durante la transpilación: {se}")
            return 1
        except Exception as e:
            mostrar_error(str(e))
            return 1
