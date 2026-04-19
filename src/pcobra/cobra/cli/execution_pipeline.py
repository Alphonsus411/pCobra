"""Pipeline compartido de análisis/ejecución para CLI Cobra."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Callable

from pcobra.cobra.core import Lexer, Parser
from pcobra.cobra.cli.i18n import _
from pcobra.core.semantic_validators import construir_cadena
from pcobra.core.semantic_validators.base import ValidadorBase


@dataclass(frozen=True)
class PipelineResult:
    """Resultado canónico del pipeline analizar+validar+ejecutar."""

    ast: Any
    resultado: Any
    validadores_extra: Any


@dataclass(frozen=True)
class InterpreterSetup:
    """Configuración derivada y componentes del intérprete para ejecución."""

    interpretador_cls: Any
    safe_mode: bool
    validadores_extra: Any
    interpretador: Any


def analizar_codigo(codigo: str) -> Any:
    """Analiza código fuente con el pipeline canónico Lexer+Parser."""

    tokens = Lexer(codigo).tokenizar()
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

    validadores_normalizados = resolver_validadores_seguridad(
        extra_validators,
        interpretador_cls=interpretador_cls,
    )
    interpretador = construir_interprete(
        interpretador_cls=interpretador_cls,
        safe_mode=safe_mode,
        extra_validators=validadores_normalizados,
    )
    return InterpreterSetup(
        interpretador_cls=interpretador_cls,
        safe_mode=bool(safe_mode),
        validadores_extra=validadores_normalizados,
        interpretador=interpretador,
    )


def ejecutar_codigo_canonico(
    codigo: str,
    *,
    interpretador: Any,
    seguro: bool,
    extra_validators: Any,
    interpretador_cls: Any,
    construir_cadena_fn: Callable[[Any], Any] = construir_cadena,
    analizar_codigo_fn: Callable[[str], Any] = analizar_codigo,
) -> PipelineResult:
    """Función canónica para analizar+validar+ejecutar código Cobra."""

    ast = analizar_codigo_fn(codigo)
    validadores_normalizados = resolver_validadores_seguridad(
        extra_validators,
        interpretador_cls=interpretador_cls,
    )
    if seguro:
        validar_ast_seguro(
            ast,
            validadores_extra=validadores_normalizados,
            construir_cadena_fn=construir_cadena_fn,
        )
    resultado = ejecutar_ast(ast, interpretador)
    return PipelineResult(
        ast=ast,
        resultado=resultado,
        validadores_extra=validadores_normalizados,
    )
