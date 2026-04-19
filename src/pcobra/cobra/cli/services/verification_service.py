from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from typing import Any
from unittest.mock import patch

from pcobra.cobra.build import backend_pipeline
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.target_policies import VERIFICATION_EXECUTABLE_TARGETS
from pcobra.cobra.core import Lexer, Parser
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.sandbox import ejecutar_en_contenedor, ejecutar_en_sandbox, ejecutar_en_sandbox_js
from pcobra.cobra.cli.utils.validators import validar_archivo_existente
from pcobra.cobra.qa.syntax_validation import SUPPORTED_VALIDATOR_TARGETS


MAX_FILE_SIZE = 10 * 1024 * 1024
VALID_EXTENSIONS = {".cobra", ".cbr", ".co"}


@dataclass
class RuntimeVerificationExecution:
    exit_code: int
    requested_targets: list[str]
    executable_targets: list[str]


def parse_verification_targets(targets_raw: str) -> list[str]:
    if not targets_raw.strip():
        return list(SUPPORTED_VALIDATOR_TARGETS)
    parsed = [item.strip().lower() for item in targets_raw.split(",") if item.strip()]
    if not parsed:
        raise ValueError(_("La lista --targets está vacía"))
    invalid = sorted(set(parsed) - set(SUPPORTED_VALIDATOR_TARGETS))
    if invalid:
        raise ValueError(_("Targets no soportados en --targets: {}.").format(", ".join(invalid)))
    return parsed


def resolve_executable_targets(requested_targets: list[str]) -> list[str]:
    return [target for target in requested_targets if target in VERIFICATION_EXECUTABLE_TARGETS]


def _compile_and_execute(ast: Any, lang: str) -> tuple[str | None, str | None]:
    try:
        code = backend_pipeline.transpile(ast, lang)
        if lang == "python":
            output = ejecutar_en_sandbox(code)
        elif lang == "javascript":
            output = ejecutar_en_sandbox_js(code)
        elif lang in {"cpp", "rust"}:
            output = ejecutar_en_contenedor(code, lang)
        else:
            return None, _("Runtime no soportado para {}").format(lang)
        return output.replace("\r\n", "\n"), None
    except ValueError:
        return None, _("Transpilador no encontrado para {}").format(lang)
    except Exception as exc:
        return None, str(exc)


def execute_runtime_verification(archivo: str, lenguajes: list[str]) -> int:
    if not lenguajes:
        raise ValueError(_("La lista de lenguajes no puede estar vacía"))

    unsupported = set(lenguajes) - set(VERIFICATION_EXECUTABLE_TARGETS)
    if unsupported:
        raise ValueError(
            _("Lenguajes no soportados: {unsupported}. Soportados: {supported}").format(
                unsupported=", ".join(sorted(unsupported)),
                supported=", ".join(VERIFICATION_EXECUTABLE_TARGETS),
            )
        )

    path = validar_archivo_existente(archivo)
    if path.suffix not in VALID_EXTENSIONS:
        raise ValueError(_("Extensión de archivo no válida. Debe ser: {}").format(", ".join(sorted(VALID_EXTENSIONS))))
    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(_("El archivo es demasiado grande (máximo {} MB)").format(MAX_FILE_SIZE // (1024 * 1024)))

    code = path.read_text(encoding="utf-8")
    tokens = Lexer(code).tokenizar()
    ast = Parser(tokens).parsear()

    with patch("sys.stdout", new_callable=StringIO) as out:
        InterpretadorCobra().ejecutar_ast(ast)
    expected = out.getvalue().replace("\r\n", "\n")

    for language in lenguajes:
        output, error = _compile_and_execute(ast, language)
        if error is not None:
            return 1
        if output != expected:
            return 1
    return 0
