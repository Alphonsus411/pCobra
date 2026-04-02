"""Políticas de modo de ejecución para comandos CLI."""

from __future__ import annotations

from argparse import Namespace

from pcobra.cobra.cli.commands.base import CommandCapability
from pcobra.cobra.cli.i18n import _

CLI_MODOS_PERMITIDOS = ("cobra", "transpilar", "mixto")
MODO_POR_DEFECTO = "mixto"

CAPABILIDADES_POR_MODO: dict[str, tuple[CommandCapability, ...]] = {
    "cobra": ("execute",),
    "transpilar": ("codegen",),
    "mixto": ("execute", "codegen", "mixed"),
}

MENSAJE_BLOQUEO_CODEGEN = _(
    "Comando de codegen no está permitido en modo '{modo}' por política de sesión. "
    "Este comando requiere transpilar/generar código (compilar, transpilar, verificar, "
    "transpilar-inverso o validar-sintaxis con perfil de transpiladores). "
    "Acción sugerida: cambia a --modo mixto o --modo transpilar "
    "(también puedes quitar --solo-cobra)."
)

# Compatibilidad para llamadas históricas por nombre/alias de comando.
CAPABILIDAD_POR_COMANDO: dict[str, CommandCapability] = {
    "ejecutar": "execute",
    "compilar": "codegen",
    "transpilar": "codegen",
    "verificar": "codegen",
    "transpilar-inverso": "codegen",
    "validar-sintaxis": "codegen",
    "qa-validar": "codegen",
}


def obtener_modo_desde_args(args: Namespace) -> str:
    """Obtiene y normaliza el modo CLI desde ``args``."""

    modo = str(getattr(args, "modo", MODO_POR_DEFECTO) or MODO_POR_DEFECTO).strip().lower()
    if modo not in CLI_MODOS_PERMITIDOS:
        return MODO_POR_DEFECTO
    return modo


def _resolver_capacidad(command_name: str, capability: CommandCapability | None) -> CommandCapability:
    if capability is not None:
        return capability
    return CAPABILIDAD_POR_COMANDO.get(command_name.strip().lower(), "mixed")


def validar_politica_modo(
    command_name: str,
    args: Namespace,
    *,
    capability: CommandCapability | None = None,
) -> None:
    """Valida si ``command_name`` puede ejecutarse en el modo actual.

    Raises:
        ValueError: si el comando no está permitido por la política de modo.
    """

    modo = obtener_modo_desde_args(args)
    comando = command_name.strip().lower()
    capacidad = _resolver_capacidad(comando, capability)
    capacidades_permitidas = CAPABILIDADES_POR_MODO[modo]

    if capacidad in capacidades_permitidas:
        return

    if modo == "cobra":
        if capacidad == "codegen":
            raise ValueError(MENSAJE_BLOQUEO_CODEGEN.format(modo=modo))
        raise ValueError(
            _(
                "El comando '{comando}' no está permitido en modo '{modo}'. "
                "En este modo se bloquea toda ruta de codegen y solo se permite ejecutar/interpretar. "
                "Cambia el modo con --modo mixto o --modo transpilar."
            ).format(comando=command_name, modo=modo)
        )

    if modo == "transpilar":
        raise ValueError(
            _(
                "El comando '{comando}' no está permitido en modo '{modo}'. "
                "En este modo solo se permite codegen (compilar/transpilar/verificar). "
                "Cambia el modo con --modo mixto o --modo cobra."
            ).format(comando=command_name, modo=modo)
        )
