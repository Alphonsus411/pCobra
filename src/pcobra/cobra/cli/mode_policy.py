"""Políticas de modo de ejecución para comandos CLI."""

from __future__ import annotations

from argparse import Namespace

from pcobra.cobra.cli.i18n import _

CLI_MODOS_PERMITIDOS = ("cobra", "transpilar", "mixto")
MODO_POR_DEFECTO = "mixto"


def obtener_modo_desde_args(args: Namespace) -> str:
    """Obtiene y normaliza el modo CLI desde ``args``."""

    modo = str(getattr(args, "modo", MODO_POR_DEFECTO) or MODO_POR_DEFECTO).strip().lower()
    if modo not in CLI_MODOS_PERMITIDOS:
        return MODO_POR_DEFECTO
    return modo


def validar_politica_modo(command_name: str, args: Namespace) -> None:
    """Valida si ``command_name`` puede ejecutarse en el modo actual.

    Raises:
        ValueError: si el comando no está permitido por la política de modo.
    """

    modo = obtener_modo_desde_args(args)
    comando = command_name.strip().lower()

    if modo == "cobra" and comando in {"compilar", "transpilar"}:
        raise ValueError(
            _(
                "El comando '{comando}' no está permitido en modo '{modo}'. "
                "En este modo solo se permite 'ejecutar'. "
                "Cambia el modo con --modo mixto o --modo transpilar."
            ).format(comando=command_name, modo=modo)
        )

    if modo == "transpilar" and comando == "ejecutar":
        raise ValueError(
            _(
                "El comando '{comando}' no está permitido en modo '{modo}'. "
                "En este modo se permite 'compilar/transpilar'. "
                "Cambia el modo con --modo mixto o --modo cobra."
            ).format(comando=command_name, modo=modo)
        )
