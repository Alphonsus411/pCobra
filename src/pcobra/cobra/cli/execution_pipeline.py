"""Pipeline compartido de análisis/ejecución para CLI Cobra.

Contrato arquitectónico relacionado:
- docs/architecture/repl-script-parity-contract.md
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Callable

from pcobra.cobra.core import Lexer, Parser
from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.unicode_sanitize import sanitize_source_for_tokenizer
from pcobra.cobra.cli.utils.validators import normalizar_validadores_extra
from pcobra.cobra.core.runtime import ValidadorBase, construir_cadena


@dataclass(frozen=True)
class PipelineResult:
    """Resultado canónico del pipeline analizar+validar+ejecutar."""

    ast: Any
    resultado: Any
    validadores_extra: Any


@dataclass(frozen=True)
class PipelineInput:
    """Entrada explícita para ejecutar el pipeline canónico completo."""

    codigo: str
    interpretador_cls: Any
    safe_mode: bool
    extra_validators: Any = None
    interpretador: Any | None = None


@dataclass(frozen=True)
class InterpreterSetup:
    """Configuración derivada y componentes del intérprete para ejecución."""

    interpretador_cls: Any
    safe_mode: bool
    validadores_extra: Any
    interpretador: Any


@dataclass(frozen=True)
class NormalizedPipelineOptions:
    """Opciones de ejecución normalizadas para el pipeline canónico."""

    safe_mode: bool
    validadores_extra: Any


def construir_script_sandbox_canonico(
    codigo: str,
    *,
    safe_mode: bool | None = None,
    extra_validators: Any = None,
    imprimir_resultado: bool = False,
) -> str:
    """Genera un script sandbox con imports canónicos del runtime Cobra."""

    extra_repr = repr(extra_validators if extra_validators is not None else None)
    safe_mode_fragment = (
        ""
        if safe_mode is None
        else f", safe_mode={safe_mode!r}, extra_validators={extra_repr}"
    )
    script = (
        "from pcobra.cobra.core import Lexer, Parser\n"
        "from pcobra.cobra.cli.utils.unicode_sanitize import sanitize_source_for_tokenizer\n"
        "from pcobra.cobra.core.runtime import InterpretadorCobra\n"
        f"_codigo = sanitize_source_for_tokenizer({codigo!r})\n"
        "_tokens = Lexer(_codigo).tokenizar()\n"
        "_ast = Parser(_tokens).parsear()\n"
        f"_interp = InterpretadorCobra({safe_mode_fragment.lstrip(', ')})\n"
        "_resultado = _interp.ejecutar_ast(_ast)\n"
    )
    if imprimir_resultado:
        script += (
            "if _resultado is not None:\n"
            "    if isinstance(_resultado, bool):\n"
            "        print('verdadero' if _resultado else 'falso')\n"
            "    else:\n"
            "        print(_resultado)\n"
        )
    return script


def analizar_codigo(codigo: str) -> Any:
    """Analiza código fuente con el pipeline canónico Lexer+Parser."""

    codigo_saneado = sanitize_source_for_tokenizer(codigo)
    tokens = Lexer(codigo_saneado).tokenizar()
    return Parser(tokens).parsear()


def ejecutar_ast(ast: Any, interpreter: Any) -> Any:
    """Ejecuta un AST usando una instancia explícita de intérprete."""

    return interpreter.ejecutar_ast(ast)


def resolver_validadores_seguridad(
    extra_validators: Any,
    *,
    interpretador_cls: Any,
) -> Any:
    """Normaliza validadores extra usando la misma política en run y REPL."""

    if extra_validators is None:
        return None
    if isinstance(extra_validators, str):
        return interpretador_cls._cargar_validadores(extra_validators)
    if isinstance(extra_validators, list) and all(
        isinstance(ruta, str) for ruta in extra_validators
    ):
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
        return acumulado
    return extra_validators


def validar_ast_seguro(
    ast: Any,
    *,
    validadores_extra: Any,
    construir_cadena_fn: Callable[[Any], Any] = construir_cadena,
) -> None:
    """Aplica la cadena de validadores de seguridad sobre el AST."""

    if validadores_extra is not None:
        if not isinstance(validadores_extra, list) or not all(
            isinstance(validador, ValidadorBase) for validador in validadores_extra
        ):
            raise TypeError(
                _("Los validadores extra deben ser una lista de instancias de validadores")
            )
    validador = construir_cadena_fn(validadores_extra)
    for nodo in ast:
        nodo.aceptar(validador)


def construir_interprete(
    *,
    interpretador_cls: Any,
    safe_mode: bool,
    extra_validators: Any,
) -> Any:
    """Construye una instancia del intérprete con la configuración común."""

    return interpretador_cls(
        safe_mode=safe_mode,
        extra_validators=extra_validators,
    )


def resolver_interpretador_cls(
    *,
    module_name: str,
    default_cls: Any,
) -> Any:
    """Obtiene la clase de intérprete desde globals del módulo (amigable a tests)."""

    module = sys.modules.get(module_name)
    if module is None:
        return default_cls
    return getattr(module, "InterpretadorCobra", default_cls)


def preparar_interpretador(
    *,
    interpretador_cls: Any,
    safe_mode: bool,
    extra_validators: Any,
) -> InterpreterSetup:
    """Centraliza normalización de validadores, flags de seguridad e intérprete."""
    opciones = normalizar_opciones_pipeline(
        safe_mode=safe_mode,
        extra_validators=extra_validators,
        interpretador_cls=interpretador_cls,
    )
    interpretador = construir_interprete(
        interpretador_cls=interpretador_cls,
        safe_mode=opciones.safe_mode,
        extra_validators=opciones.validadores_extra,
    )
    return InterpreterSetup(
        interpretador_cls=interpretador_cls,
        safe_mode=opciones.safe_mode,
        validadores_extra=opciones.validadores_extra,
        interpretador=interpretador,
    )


def normalizar_opciones_pipeline(
    *,
    safe_mode: bool,
    extra_validators: Any,
    interpretador_cls: Any,
) -> NormalizedPipelineOptions:
    """Punto único para normalizar safe_mode y extra_validators del pipeline."""

    safe_mode_normalizado = bool(safe_mode)
    extra_validators_normalizados = normalizar_validadores_extra(extra_validators)
    validadores_resueltos = resolver_validadores_seguridad(
        extra_validators_normalizados,
        interpretador_cls=interpretador_cls,
    )
    return NormalizedPipelineOptions(
        safe_mode=safe_mode_normalizado,
        validadores_extra=validadores_resueltos,
    )


def ejecutar_codigo_canonico(
    codigo: str,
    *,
    interpretador: Any,
    seguro: bool,
    extra_validators: Any,
    construir_cadena_fn: Callable[[Any], Any] = construir_cadena,
    analizar_codigo_fn: Callable[[str], Any] = analizar_codigo,
) -> PipelineResult:
    """Función canónica para analizar+validar+ejecutar código Cobra."""

    ast = analizar_codigo_fn(codigo)
    if seguro:
        validar_ast_seguro(
            ast,
            validadores_extra=extra_validators,
            construir_cadena_fn=construir_cadena_fn,
        )
    resultado = ejecutar_ast(ast, interpretador)
    return PipelineResult(
        ast=ast,
        resultado=resultado,
        validadores_extra=extra_validators,
    )


def ejecutar_pipeline_explicito(
    pipeline_input: PipelineInput,
    *,
    construir_cadena_fn: Callable[[Any], Any] = construir_cadena,
    analizar_codigo_fn: Callable[[str], Any] = analizar_codigo,
) -> tuple[InterpreterSetup, PipelineResult]:
    """API única y explícita para análisis, validación, preparación y ejecución.

    Flujo:
    1) Analizar ``codigo``.
    2) Validar AST si ``safe_mode`` está activo.
    3) Preparar intérprete (o reutilizar uno provisto para estado persistente).
    4) Ejecutar AST.
    """

    setup = preparar_interpretador(
        interpretador_cls=pipeline_input.interpretador_cls,
        safe_mode=pipeline_input.safe_mode,
        extra_validators=pipeline_input.extra_validators,
    )
    interpretador = (
        pipeline_input.interpretador
        if pipeline_input.interpretador is not None
        else setup.interpretador
    )
    resultado = ejecutar_codigo_canonico(
        pipeline_input.codigo,
        interpretador=interpretador,
        seguro=setup.safe_mode,
        extra_validators=setup.validadores_extra,
        construir_cadena_fn=construir_cadena_fn,
        analizar_codigo_fn=analizar_codigo_fn,
    )
    setup_final = InterpreterSetup(
        interpretador_cls=setup.interpretador_cls,
        safe_mode=setup.safe_mode,
        validadores_extra=setup.validadores_extra,
        interpretador=interpretador,
    )
    return setup_final, resultado
