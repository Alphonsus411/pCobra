"""Política de deprecación progresiva para targets/comandos avanzados."""

from __future__ import annotations

import logging
import os
from argparse import Namespace

from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.messages import mostrar_advertencia

DEPRECATED_PUBLIC_TARGETS: tuple[str, ...] = ("wasm", "go", "cpp", "java", "asm")
DEPRECATION_PHASE_ENV = "COBRA_TARGET_DEPRECATION_PHASE"
LEGACY_TARGETS_MODE_ENV = "COBRA_LEGACY_TARGETS_MODE"


def current_deprecation_phase() -> int:
    """Fase activa de deprecación (1 o 2)."""
    raw = (os.environ.get(DEPRECATION_PHASE_ENV, "1") or "1").strip()
    try:
        phase = int(raw)
    except ValueError:
        return 1
    if phase < 1:
        return 1
    if phase > 2:
        return 2
    return phase


def is_legacy_targets_mode(args: Namespace | object | None) -> bool:
    """Determina si la ejecución habilitó modo legacy para targets deprecated."""
    env_enabled = (os.environ.get(LEGACY_TARGETS_MODE_ENV, "") or "").strip() == "1"
    arg_enabled = bool(getattr(args, "legacy_targets", False)) if args is not None else False
    return env_enabled or arg_enabled


def visible_public_targets(targets: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    """Targets visibles en help público según fase."""
    phase = current_deprecation_phase()
    if phase < 2:
        return tuple(targets)
    return tuple(target for target in targets if target not in DEPRECATED_PUBLIC_TARGETS)


def emit_target_deprecation_event(*, command: str, target: str, phase: int, legacy_mode: bool) -> None:
    """Telemetría mínima de uso de targets deprecated vía logging estructurado."""
    logging.getLogger(__name__).warning(
        "target_deprecation_usage command=%s target=%s phase=%s legacy_mode=%s",
        command,
        target,
        phase,
        legacy_mode,
    )


def enforce_target_deprecation_policy(*, command: str, target: str, args: Namespace | object | None) -> None:
    """Aplica política en 2 fases para targets deprecated."""
    canonical = str(target).strip().lower()
    if canonical not in DEPRECATED_PUBLIC_TARGETS:
        return

    phase = current_deprecation_phase()
    legacy_mode = is_legacy_targets_mode(args)
    emit_target_deprecation_event(command=command, target=canonical, phase=phase, legacy_mode=legacy_mode)

    if phase == 1:
        mostrar_advertencia(
            _(
                "Target '{target}' deprecado (Fase 1): se mantiene por compatibilidad interna, "
                "pero será ocultado del help público y quedará solo en modo legacy en Fase 2."
            ).format(target=canonical)
        )
        return

    if not legacy_mode:
        raise ValueError(
            _(
                "Target '{target}' está en Fase 2 de deprecación y ya no forma parte del modo público. "
                "Use --legacy-targets o {env}=1 para compatibilidad legacy."
            ).format(target=canonical, env=LEGACY_TARGETS_MODE_ENV)
        )

    mostrar_advertencia(
        _(
            "Target '{target}' ejecutado en modo legacy (Fase 2). Esta ruta existe solo por compatibilidad interna."
        ).format(target=canonical)
    )


def enforce_advanced_profile_policy(*, command: str, args: Namespace | object | None) -> None:
    """Restringe comandos avanzados durante Fase 2 al perfil legado/avanzado."""
    phase = current_deprecation_phase()
    profile = str(getattr(args, "perfil", "publico") or "publico").strip().lower()
    legacy_mode = is_legacy_targets_mode(args)
    logging.getLogger(__name__).warning(
        "advanced_command_usage command=%s profile=%s phase=%s legacy_mode=%s",
        command,
        profile,
        phase,
        legacy_mode,
    )
    if phase < 2:
        if profile != "avanzado":
            mostrar_advertencia(
                _("El comando '{command}' expone capacidades avanzadas de backend; use --perfil avanzado.").format(
                    command=command
                )
            )
        return

    if profile != "avanzado" and not legacy_mode:
        raise ValueError(
            _(
                "El comando '{command}' está oculto del perfil público en Fase 2. "
                "Use --perfil avanzado (o modo legacy) para mantener compatibilidad."
            ).format(command=command)
        )
