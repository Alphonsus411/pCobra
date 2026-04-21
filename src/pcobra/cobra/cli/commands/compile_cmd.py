import multiprocessing
import os
from argparse import ArgumentTypeError

from pcobra.cobra.build import backend_pipeline
from pcobra.cobra.cli.target_policies import (
    OFFICIAL_TRANSPILATION_TARGETS,
    add_internal_legacy_targets_flag,
    enabled_internal_legacy_targets,
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
from pcobra.cobra.cli.transpiler_registry import cli_transpiler_targets
from pcobra.cobra.transpilers import registry as transpiler_registry
from pcobra.cobra.cli.deprecation_policy import (
    enforce_target_deprecation_policy,
    visible_public_targets,
)
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

LANG_CHOICES = cli_transpiler_targets()


def register_transpiler_backend(backend: str, transpiler_cls, *, context: str) -> str:
    """Compatibilidad: delega registro de plugins al registro consolidado."""
    return transpiler_registry.register_transpiler_backend(
        backend,
        transpiler_cls,
        context=context,
    )


def load_entrypoint_transpilers() -> tuple[int, int, int]:
    """Compatibilidad: delega carga de entry points al registro consolidado."""
    return transpiler_registry.load_entrypoint_transpilers()


def _ensure_entrypoints_loaded_once() -> None:
    """Compatibilidad: delega carga idempotente al registro consolidado."""
    transpiler_registry.ensure_entrypoint_transpilers_loaded_once()

def _validate_official_backend_or_raise(backend: str, *, context: str) -> str:
    """Validador único de backend oficial conectado a la matriz canónica."""
    try:
        return parse_target(backend)
    except ArgumentTypeError as exc:
        raise ValueError(str(exc)) from exc

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
    plugin_cls = transpiler_registry.plugin_transpilers().get(lang)
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
        lang_choices = list(LANG_CHOICES) + list(enabled_internal_legacy_targets())
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
