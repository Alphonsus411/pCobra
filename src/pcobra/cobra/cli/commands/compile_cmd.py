import logging
import multiprocessing
import os
from argparse import ArgumentTypeError
from importlib import import_module
from importlib.metadata import entry_points

from pcobra.cobra.transpilers import module_map
from pcobra.cobra.cli.target_policies import (
    OFFICIAL_TRANSPILATION_TARGETS,
    parse_target,
    parse_target_list,
)
from pcobra.cobra.transpilers.registry import (
    build_official_transpilers,
    official_transpiler_targets,
)
from pcobra.cobra.transpilers.target_utils import (
    build_target_help_by_tier,
    require_official_target_subset,
    resolution_candidates,
    target_label,
)
from pcobra.core.ast_cache import obtener_ast
from pcobra.core.sandbox import validar_dependencias
from pcobra.core.semantic_validators import (
    PrimitivaPeligrosaError,
    construir_cadena,
)
from pcobra.cobra.cli.commands.base import BaseCommand
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.utils.validators import validar_archivo_existente
from pcobra.cobra.cli.utils.autocomplete import files_completer
from pcobra.cobra.core import ParserError
from pcobra.core.cobra_config import tiempo_max_transpilacion

# Constantes de configuración
MAX_PROCESSES = 4
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
PROCESS_TIMEOUT = tiempo_max_transpilacion()
MAX_LANGUAGES = 10

TRANSPILERS = build_official_transpilers()


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
    TRANSPILERS[canonical] = transpiler_cls
    return canonical


def _validate_official_backend_or_raise(backend: str, *, context: str) -> str:
    """Valida backend contra la whitelist oficial y devuelve su forma canónica."""
    try:
        canonical = parse_target(backend)
    except ArgumentTypeError as exc:
        raise ValueError(str(exc)) from exc
    if canonical not in require_official_target_subset(
        OFFICIAL_TRANSPILATION_TARGETS,
        context=f"compile_cmd::{context}",
    ):
        raise ValueError(
            _("Backend no permitido en {context}: {backend}. Permitidos: {supported}").format(
                context=context,
                backend=backend,
                supported=", ".join(OFFICIAL_TRANSPILATION_TARGETS),
            )
        )
    return canonical


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



def load_entrypoint_transpilers() -> None:
    """Carga entry points de transpiladores sin permitir aliases o targets no oficiales."""
    for ep in _iter_transpiler_entry_points():
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
            if normalized_ep_name in TRANSPILERS:
                logging.warning(
                    "Plugin de transpilador '%s' omitido: '%s' ya existe en el registro canónico",
                    ep.name,
                    normalized_ep_name,
                )
                continue
            register_transpiler_backend(normalized_ep_name, cls, context="plugins(entry_points)")
        except ValueError as exc:
            logging.error(
                "Plugin de transpilador '%s' rechazado por política oficial: %s",
                ep.name,
                exc,
            )
        except Exception as exc:
            logging.error("Error cargando transpilador %s: %s", ep.name, exc)


load_entrypoint_transpilers()

LANG_CHOICES = list(official_transpiler_targets())
TARGETS_HELP = build_target_help_by_tier(tuple(LANG_CHOICES))


def parse_official_target_list(value: str) -> list[str]:
    """Normaliza una lista de targets y asegura que sean oficiales."""
    parsed_targets = parse_target_list(value)
    official_subset = require_official_target_subset(
        OFFICIAL_TRANSPILATION_TARGETS,
        context="compile_cmd::parse_official_target_list",
    )
    unsupported_targets = [target for target in parsed_targets if target not in official_subset]
    if unsupported_targets:
        raise ArgumentTypeError(
            _("Targets no soportados: {targets}. Soportados: {supported}").format(
                targets=", ".join(unsupported_targets),
                supported=", ".join(LANG_CHOICES),
            )
        )
    return parsed_targets

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
    last_error = None
    for candidate in resolution_candidates(backend):
        try:
            validar_dependencias(candidate, mod_info)
            return
        except (ValueError, FileNotFoundError) as exc:
            last_error = exc
    if last_error is not None:
        raise last_error


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

    def register_subparser(self, subparsers):
        """Registra los argumentos del subcomando."""
        parser = subparsers.add_parser(
            self.name,
            help=_("Transpila un archivo"),
            aliases=["transpilar"],
        )
        parser.add_argument("archivo").completer = files_completer()
        parser.add_argument(
            "--tipo",
            type=parse_target,
            choices=LANG_CHOICES,
            default="python",
            help=_("Tipo de código generado ({targets}).").format(targets=TARGETS_HELP),
        )
        parser.add_argument(
            "--backend",
            type=parse_target,
            choices=LANG_CHOICES,
            help=_("Alias de --tipo ({targets}).").format(targets=TARGETS_HELP),
        )
        parser.add_argument(
            "--tipos",
            type=parse_official_target_list,
            help=_("Lista de lenguajes separados por comas ({targets}).").format(targets=TARGETS_HELP),
        )
        parser.set_defaults(cmd=self)
        return parser

    def _ejecutar_transpilador(self, parametros: tuple) -> tuple:
        """Ejecuta un transpilador específico."""
        lang, ast = parametros
        transp = TRANSPILERS[lang]()
        return lang, transp.__class__.__name__, transp.generate_code(ast)

    def run(self, args):
        """Ejecuta la lógica del comando."""
        archivo = args.archivo

        try:
            validate_file(archivo)
        except ValueError as e:
            mostrar_error(str(e))
            return 1

        tipos_argument = getattr(args, "tipos", None)
        if isinstance(tipos_argument, str):
            try:
                tipos_argument = parse_official_target_list(tipos_argument)
            except ArgumentTypeError as parse_error:
                mostrar_error(str(parse_error))
                return 1

        mod_info = module_map.get_toml_map()
        try:
            transpilador_objetivo = _validate_official_backend_or_raise(
                getattr(args, "backend", None) or args.tipo,
                context="CLI",
            )
        except ValueError as validation_err:
            mostrar_error(str(validation_err))
            return 1

        try:
            if tipos_argument:
                langs = list(tipos_argument)
                for lang in langs:
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
                    if lang not in TRANSPILERS:
                        raise ValueError(_("Transpilador no soportado."))
                
                try:
                    resultados = run_transpiler_pool(lenguajes, ast, self._ejecutar_transpilador)
                    for lang, nombre, resultado in resultados:
                        mostrar_info(
                            _("Código generado ({nombre}) para {lang}:").format(
                                nombre=nombre,
                                lang=f"{target_label(lang)} ({lang})",
                            )
                        )
                        print(resultado)
                except multiprocessing.TimeoutError:
                    mostrar_error(_("Tiempo de ejecución excedido"))
                    return 1
            else:
                transpilador = transpilador_objetivo
                if transpilador not in TRANSPILERS:
                    raise ValueError(_("Transpilador no soportado."))
                transp = TRANSPILERS[transpilador]()
                resultado = transp.generate_code(ast)
                mostrar_info(
                    _("Código generado ({name}):").format(
                        name=transp.__class__.__name__
                    )
                )
                print(resultado)
            return 0

        except PrimitivaPeligrosaError as pe:
            logging.error("Primitiva peligrosa: %s", pe)
            mostrar_error(str(pe))
            return 1
        except ParserError as se:
            logging.error("Error de sintaxis durante la transpilación: %s", se)
            mostrar_error(f"Error durante la transpilación: {se}")
            return 1
        except Exception as e:
            logging.error("Error general durante la transpilación: %s", e)
            mostrar_error(str(e))
            return 1
