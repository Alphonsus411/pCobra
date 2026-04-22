import concurrent.futures
import logging
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import patch

from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.sandbox import ejecutar_en_contenedor, ejecutar_en_sandbox, ejecutar_en_sandbox_js
from pcobra.cobra.build import backend_pipeline
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.mode_policy import validar_politica_modo
from pcobra.cobra.cli.target_policies import (
    OFFICIAL_TRANSPILATION_TARGETS,
    VERIFICATION_EXECUTABLE_TARGETS,
)
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.cli.utils.validators import validar_archivo_existente
from pcobra.cobra.core import Lexer, Parser

MAX_FILE_SIZE = 10 * 1024 * 1024
VALID_EXTENSIONS = {".cobra", ".cbr", ".co"}


def target_cli_choices(values: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(values)


class TestService:
    OFFICIAL_LANGUAGE_CHOICES = target_cli_choices(OFFICIAL_TRANSPILATION_TARGETS)
    SUPPORTED_LANGUAGES = target_cli_choices(VERIFICATION_EXECUTABLE_TARGETS)

    def __init__(self) -> None:
        self._interprete = InterpretadorCobra()
        self._logger = logging.getLogger(__name__)

    def run(self, args: Any) -> int:
        try:
            validar_politica_modo("verificar", args, capability="codegen")

            if not args.archivo or not args.lenguajes:
                raise ValueError(_("Se requieren archivo y lenguajes"))

            lenguajes = list(args.lenguajes)
            self.validate_languages(lenguajes)

            codigo = self.read_source_file(args.archivo)
            tokens = Lexer(codigo).tokenizar()
            ast = Parser(tokens).parsear()

            with patch("sys.stdout", new_callable=StringIO) as out:
                self._interprete.ejecutar_ast(ast)
            esperado = out.getvalue().replace("\r\n", "\n")

            diferencias: Dict[str, str] = {}
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futuros = {
                    executor.submit(self.verify_language, lang, ast, esperado): lang for lang in lenguajes
                }

                for futuro in concurrent.futures.as_completed(futuros):
                    lang, error = futuro.result()
                    if error:
                        diferencias[lang] = error

            if diferencias:
                mostrar_error(_("Se encontraron diferencias:"))
                for lang, salida in diferencias.items():
                    mostrar_error(f"{lang}: {salida.strip()}")
                return 1

            mostrar_info(_("Todas las salidas coinciden"))
            return 0

        except (ValueError, PermissionError) as e:
            mostrar_error(str(e))
            return 1
        except Exception as e:
            self._logger.exception("Error inesperado")
            mostrar_error(f"Error inesperado: {str(e)}")
            return 1

    def validate_languages(self, languages: List[str]) -> None:
        if not languages:
            raise ValueError(_("La lista de lenguajes no puede estar vacía"))

        unsupported = set(languages) - set(self.SUPPORTED_LANGUAGES)
        if unsupported:
            raise ValueError(
                _("Lenguajes no soportados: {unsupported}. Soportados: {supported}").format(
                    unsupported=", ".join(sorted(unsupported)),
                    supported=", ".join(self.SUPPORTED_LANGUAGES),
                )
            )

    def validate_file(self, file_path: str) -> None:
        path = Path(file_path)
        if path.suffix not in VALID_EXTENSIONS:
            raise ValueError(_("Extensión de archivo no válida. Debe ser: {}").format(", ".join(sorted(VALID_EXTENSIONS))))

        if path.stat().st_size > MAX_FILE_SIZE:
            raise ValueError(_("El archivo es demasiado grande (máximo {} MB)").format(MAX_FILE_SIZE // (1024 * 1024)))

    def read_source_file(self, file_path: str) -> str:
        validar_archivo_existente(file_path)
        self.validate_file(file_path)

        try:
            return Path(file_path).read_text(encoding="utf-8")
        except PermissionError:
            raise PermissionError(_("No hay permisos para leer el archivo '{}'").format(file_path))
        except UnicodeDecodeError as e:
            self._logger.error("Error decodificando archivo: %s", str(e))
            raise ValueError(_("Error al decodificar el archivo '{}'").format(file_path))

    def compile_and_execute(self, ast: Any, lang: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            codigo_gen = backend_pipeline.transpile(ast, lang)

            if lang == "python":
                salida = ejecutar_en_sandbox(codigo_gen)
            elif lang == "javascript":
                salida = ejecutar_en_sandbox_js(codigo_gen)
            elif lang in {"cpp", "rust"}:
                salida = ejecutar_en_contenedor(codigo_gen, lang)
            else:
                return None, _("Runtime no soportado para {}").format(lang)

            return salida.replace("\r\n", "\n"), None

        except ValueError:
            return None, _("Transpilador no encontrado para {}").format(lang)
        except Exception as e:
            self._logger.error("Error en %s: %s", lang, str(e))
            return None, str(e)

    def verify_language(self, lang: str, ast: Any, esperado: str) -> Tuple[str, Optional[str]]:
        salida, error = self.compile_and_execute(ast, lang)

        if error:
            return lang, error
        if salida != esperado:
            return lang, salida

        return lang, None
