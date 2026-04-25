import logging
import os
from argparse import ArgumentParser, Namespace
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Optional, Type

try:  # pragma: no cover - dependencia opcional
    from chardet import detect as _detect_encoding
except ModuleNotFoundError:  # pragma: no cover - entornos sin chardet
    _detect_encoding = None

try:  # pragma: no cover - dependencia opcional
    from jsonschema import ValidationError as _JSONSchemaValidationError
except ModuleNotFoundError:  # pragma: no cover - entornos sin jsonschema
    _JSONSchemaValidationError = None
    class _FallbackValidationError(RuntimeError):
        """Excepción básica usada cuando falta jsonschema."""

        pass
else:
    class _FallbackValidationError(_JSONSchemaValidationError):  # type: ignore[misc]
        pass

ValidationError = _FallbackValidationError

import pcobra.cobra.transpilers.reverse as reverse_module
from pcobra.cobra.transpilers.reverse.policy import (
    normalize_reverse_language,
    parse_reverse_source_language,
)
from pcobra.cobra.cli.commands.base import BaseCommand, CommandError
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.mode_policy import validar_politica_modo
from pcobra.cobra.cli.deprecation_policy import (
    enforce_advanced_profile_policy,
    enforce_target_deprecation_policy,
    visible_public_targets,
)
from pcobra.cobra.cli.utils.argument_parser import CustomArgumentParser
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.target_policies import (
    OFFICIAL_TRANSPILATION_TARGETS,
    add_internal_legacy_targets_flag,
    parse_target,
)
from pcobra.cobra.transpilers.import_helper import get_standard_imports
from pcobra.cobra.build import backend_pipeline
from pcobra.cobra.cli.transpiler_registry import cli_transpilers, cli_transpiler_targets
from pcobra.cobra.cli.utils.validators import validar_archivo_existente
from pcobra.cobra.transpilers.target_utils import (
    build_target_help_by_tier,
)
from pcobra.cobra.transpilers.targets import OFFICIAL_TARGETS

# Configuración del logging
logger = logging.getLogger(__name__)

# Constantes
MAX_FILE_SIZE = 1024 * 1024  # 1MB
EXTENSIONES_POR_LENGUAJE: Dict[str, str] = {
    "python": ".py",
    "javascript": ".js",
    "java": ".java",
}

class UnsupportedLanguageError(Exception):
    """Error lanzado cuando se intenta usar un lenguaje no soportado."""
    pass

class TranspilationError(Exception):
    """Error lanzado cuando ocurre un problema durante la transpilación."""
    pass


def _normalize_ast_for_roundtrip(value: Any) -> Any:
    """Normaliza nodos AST para comparaciones de round-trip estables."""
    if is_dataclass(value):
        return _normalize_ast_for_roundtrip(asdict(value))
    if isinstance(value, dict):
        return {
            key: _normalize_ast_for_roundtrip(val)
            for key, val in sorted(value.items(), key=lambda item: item[0])
        }
    if isinstance(value, (list, tuple)):
        return [_normalize_ast_for_roundtrip(item) for item in value]
    if hasattr(value, "__dict__"):
        return _normalize_ast_for_roundtrip(vars(value))
    return value


def _build_roundtrip_loss_report(
    *,
    destino: str,
    ast_original: Any,
    codigo_generado: str,
) -> Optional[str]:
    """Genera un reporte de degradación comparando AST original vs round-trip."""
    reverse_cls = REVERSE_TRANSPILERS.get(destino)
    if reverse_cls is None:
        return (
            f"[round-trip] No hay parser inverso para destino '{destino}', "
            "no se puede medir degradación automáticamente."
        )

    reverse_dest = reverse_cls()
    imports_estandar = get_standard_imports(destino) or ""
    codigo_para_reverse = codigo_generado
    if imports_estandar and codigo_generado.startswith(imports_estandar):
        codigo_para_reverse = codigo_generado[len(imports_estandar):]
    try:
        ast_reconstruido = reverse_dest.generate_ast(codigo_para_reverse)
    except NotImplementedError as exc:
        return (
            "[round-trip] Conversión parcial detectada: el parser inverso del destino "
            f"'{destino}' no soporta un nodo generado ({exc})."
        )
    except Exception as exc:  # pragma: no cover - defensa adicional
        return (
            "[round-trip] No fue posible reconstruir AST para validar pérdida "
            f"de información en destino '{destino}': {exc}"
        )

    original_norm = _normalize_ast_for_roundtrip(ast_original)
    reconstruido_norm = _normalize_ast_for_roundtrip(ast_reconstruido)
    if original_norm != reconstruido_norm:
        return (
            "[round-trip] Posible degradación semántica/sintáctica: "
            f"AST normalizado distinto tras {destino} -> Cobra."
        )
    return None


REVERSE_TRANSPILERS: Dict[str, Type] = {
    language: reverse_module.REGISTERED_REVERSE_TRANSPILERS[language]
    for language in reverse_module.REVERSE_SCOPE_LANGUAGES
    if language in reverse_module.REGISTERED_REVERSE_TRANSPILERS
}
ORIGIN_CHOICES = tuple(reverse_module.REVERSE_SCOPE_LANGUAGES)
TARGETS_HELP = build_target_help_by_tier(
    tuple(visible_public_targets(OFFICIAL_TRANSPILATION_TARGETS))
)
REVERSE_ORIGINS_HELP = ", ".join(ORIGIN_CHOICES)


def _runtime_transpilers() -> Dict[str, Type]:
    """Consulta en runtime el registro canónico para evitar snapshots a nivel módulo."""
    return dict(cli_transpilers())


def _runtime_destino_choices() -> tuple[str, ...]:
    """Consulta targets canónicos en runtime para evitar snapshots estáticos."""
    return cli_transpiler_targets()


def _validate_official_target_or_raise(target: str, *, context: str) -> str:
    """Valida que un target pertenezca a la whitelist oficial."""
    canonical = parse_target(target)
    if canonical not in OFFICIAL_TARGETS:
        raise UnsupportedLanguageError(
            "Lenguaje de destino fuera de Tier 1/Tier 2 en {context}: "
            "'{target}'. Usa uno de: {allowed}".format(
                context=context,
                target=target,
                allowed=", ".join(_runtime_destino_choices()),
            )
        )
    return canonical


def validar_consistencia_reverse_transpilers() -> None:
    """Valida que la CLI y el registro interno compartan la misma política."""
    policy = set(reverse_module.REVERSE_SCOPE_LANGUAGES)
    registry = set(reverse_module.REGISTERED_REVERSE_TRANSPILERS.keys())
    cli = set(REVERSE_TRANSPILERS.keys())
    if (
        cli != registry
        or tuple(ORIGIN_CHOICES) != tuple(reverse_module.REVERSE_SCOPE_LANGUAGES)
        or not registry.issubset(policy)
    ):
        raise RuntimeError(
            "Inconsistencia de reverse transpilers: "
            "policy={policy}, registry={registry}, cli={cli}, choices={choices}".format(
                policy=sorted(policy),
                registry=sorted(registry),
                cli=sorted(cli),
                choices=tuple(ORIGIN_CHOICES),
            )
        )


validar_consistencia_reverse_transpilers()

@contextmanager
def archivo_fuente(ruta: str, codificacion: str):
    """Context manager para manejar la apertura y cierre de archivos.
    
    Args:
        ruta: Ruta al archivo
        codificacion: Codificación del archivo
        
    Yields:
        El archivo abierto
        
    Raises:
        OSError: Si hay problemas al abrir el archivo
    """
    try:
        with open(ruta, 'r', encoding=codificacion) as f:
            yield f
    except Exception as e:
        logger.error(f"Error al leer archivo: {e}")
        raise

class TranspilarInversoCommand(BaseCommand):
    """Convierte código desde un origen reverse de entrada hacia un target oficial.
    
    Esta clase implementa un comando que permite leer código desde uno de los
    orígenes reverse mantenidos por política y generar salida en uno de los 8
    targets oficiales de transpilación, pasando por el AST de Cobra.
    """

    name: str = "transpilar-inverso"
    capability: str = "codegen"

    def register_subparser(self, subparsers: Any) -> CustomArgumentParser:
        """Registra los argumentos del subcomando en el parser.
        
        Args:
            subparsers: Objeto para registrar subcomandos
            
        Returns:
            CustomArgumentParser: Parser configurado para el subcomando
        """
        parser = subparsers.add_parser(
            self.name,
            help=_("Convierte desde un origen reverse de entrada hacia un target oficial de salida"),
        )
        parser.add_argument(
            "archivo",
            help=_("Ruta al archivo fuente a transpilar")
        )
        parser.add_argument(
            "--origen",
            help=_(
                "Lenguaje de origen para transpilación inversa "
                "(solo orígenes reverse de entrada: {})"
            ).format(
                REVERSE_ORIGINS_HELP
            ),
            required=True,
            type=parse_reverse_source_language,
            choices=ORIGIN_CHOICES,
        )
        parser.add_argument(
            "--destino",
            help=_(
                "Target oficial de salida (registro/transpilación canónica): {targets}."
            ).format(
                targets=TARGETS_HELP,
            ),
            required=True,
            type=parse_target,
            choices=_runtime_destino_choices(),
        )
        add_internal_legacy_targets_flag(parser)
        parser.add_argument(
            "--perfil",
            choices=("publico", "avanzado"),
            default="avanzado",
            help=_("Perfil del comando: 'avanzado' para rutas reverse/backend."),
        )
        parser.set_defaults(cmd=self)
        return parser

    def _validar_archivo(self, archivo: str, lenguaje: str) -> Optional[str]:
        """Valida que el archivo exista y sea legible.
        
        Args:
            archivo: Ruta al archivo a validar
            lenguaje: Lenguaje de origen esperado
            
        Returns:
            Optional[str]: Mensaje de error si hay problemas, None si todo está bien
        """
        if not os.path.isfile(archivo):
            return f"'{archivo}' no es un archivo regular"
        if not os.access(archivo, os.R_OK):
            return f"No hay permisos de lectura para '{archivo}'"
        if os.path.getsize(archivo) > MAX_FILE_SIZE:
            return f"El archivo '{archivo}' excede el tamaño máximo permitido ({MAX_FILE_SIZE} bytes)"
            
        extension_esperada = EXTENSIONES_POR_LENGUAJE.get(lenguaje)
        if extension_esperada and not archivo.lower().endswith(extension_esperada):
            return f"El archivo '{archivo}' no tiene la extensión esperada para {lenguaje} ({extension_esperada})"
        
        return None

    def _detectar_codificacion(self, archivo: str) -> str:
        """Detecta la codificación del archivo.
        
        Args:
            archivo: Ruta al archivo
            
        Returns:
            str: Codificación detectada
        """
        if _detect_encoding is None:
            logger.debug(
                "chardet no está instalado; se asumirá codificación utf-8 para %s",
                archivo,
            )
            return "utf-8"

        with open(archivo, "rb") as f:
            raw_data = f.read()
        resultado = _detect_encoding(raw_data)
        encoding = resultado.get("encoding") if isinstance(resultado, dict) else None
        if not encoding:
            logger.warning(
                "No se pudo detectar la codificación para %s, usando utf-8", archivo
            )
            encoding = "utf-8"
        return encoding

    def _verificar_dependencias(self, origen: str, destino: str) -> None:
        """Verifica que los transpiladores necesarios estén disponibles.
        
        Args:
            origen: Lenguaje de origen
            destino: Lenguaje de destino
            
        Raises:
            UnsupportedLanguageError: Si algún transpilador no está disponible
        """
        if origen not in REVERSE_TRANSPILERS:
            raise UnsupportedLanguageError(
                f"No hay parser reverse disponible para el lenguaje de origen '{origen}'"
            )
        transpilers = _runtime_transpilers()
        if destino not in transpilers:
            raise UnsupportedLanguageError(
                f"No hay transpilador oficial disponible para el lenguaje de destino '{destino}'"
            )
        _validate_official_target_or_raise(destino, context="CLI transpilar-inverso")

    def _validar_origen_en_politica(self, origen: str) -> None:
        """Valida que el origen esté dentro de la política de reverse transpilation."""
        permitidos = set(reverse_module.REVERSE_SCOPE_LANGUAGES)
        if origen not in permitidos:
            sugeridos = ", ".join(ORIGIN_CHOICES)
            raise UnsupportedLanguageError(
                "Origen fuera de política de transpilación inversa: "
                f"'{origen}'. Usa uno de los orígenes reverse de entrada: {sugeridos}"
            )

    def run(self, args: Namespace) -> int:
        """Ejecuta la transpilación del código.
        
        Args:
            args: Argumentos parseados del comando
            
        Returns:
            int: 0 si la ejecución fue exitosa, otro valor en caso de error
            
        Raises:
            CommandError: Si hay errores en la validación o transpilación
        """
        try:
            validar_politica_modo(self.name, args, capability=self.capability)
            enforce_advanced_profile_policy(command=self.name, args=args)

            origen = normalize_reverse_language(args.origen)
            destino = _validate_official_target_or_raise(
                args.destino,
                context="CLI transpilar-inverso",
            )
            enforce_target_deprecation_policy(
                command=self.name,
                target=destino,
                args=args,
            )

            self._validar_origen_en_politica(origen)

            logger.debug(f"Iniciando validación del archivo {args.archivo}")

            validar_archivo_existente(args.archivo)

            # Validar archivo
            if error := self._validar_archivo(args.archivo, origen):
                raise CommandError(error)

            # Verificar dependencias
            self._verificar_dependencias(origen, destino)

            # Validar transpiladores
            reverse_cls = REVERSE_TRANSPILERS.get(origen)
            transpilers = _runtime_transpilers()
            transp_cls = transpilers.get(destino)

            logger.debug(
                f"Usando transpilador {reverse_cls.__name__} para origen {origen}"
            )
            logger.debug(
                f"Usando transpilador {transp_cls.__name__} para destino {destino}"
            )

            # Detectar codificación y leer archivo
            codificacion = self._detectar_codificacion(args.archivo)
            logger.debug(f"Codificación detectada para {args.archivo}: {codificacion}")

            with archivo_fuente(args.archivo, codificacion) as f:
                contenido = f.read()
                if not contenido.strip():
                    raise ValidationError(f"El archivo '{args.archivo}' está vacío")

            # Transpilar código
            logger.info(
                "Iniciando transpilación inversa desde origen reverse %s hacia target oficial %s",
                origen,
                destino,
            )
            ast = reverse_cls().load_file(args.archivo)
            codigo = backend_pipeline.transpile(ast, destino)
            report = _build_roundtrip_loss_report(
                destino=destino,
                ast_original=ast,
                codigo_generado=codigo,
            )

            mostrar_info(
                _("Código transpilado a target oficial ({name}) desde origen reverse {origin}:").format(
                    name=transp_cls.__name__,
                    origin=origen,
                )
            )
            print(codigo)
            if report:
                mostrar_info(report)
            if destino == "python":
                lineas = codigo.splitlines()
                previsualizacion = [linea.replace("'", "") for linea in lineas]
                if previsualizacion != lineas:
                    print("# Vista previa sin comillas:")
                    print("\n".join(previsualizacion))
            return 0

        except (UnicodeDecodeError, UnicodeError) as exc:
            logger.error(f"Error de codificación: {exc}", exc_info=True)
            mostrar_error(f"Error de codificación al leer '{args.archivo}'")
            return 1
        except OSError as exc:
            if isinstance(exc, FileNotFoundError):
                raise
            logger.error(f"Error de E/S: {exc}", exc_info=True)
            mostrar_error(f"Error al leer el archivo: {exc}")
            return 1
        except NotImplementedError as exc:
            logger.error(f"Funcionalidad no implementada: {exc}", exc_info=True)
            mostrar_error(
                "Transpilación inversa con pérdida de información: "
                f"nodo/constructo no soportado ({exc})"
            )
            return 1
        except (CommandError, ValidationError, UnsupportedLanguageError, ValueError) as exc:
            mostrar_error(str(exc))
            return 1
        except TranspilationError as exc:
            logger.error(f"Error en transpilación: {exc}", exc_info=True)
            mostrar_error(f"Error al transpilar el código: {exc}")
            return 1
        except Exception as exc:
            logger.error(f"Error inesperado: {exc}", exc_info=True)
            mostrar_error(f"Error inesperado: {exc}")
            return 1
