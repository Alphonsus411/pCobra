"""Feature flags internas para opciones legacy de CLI."""

from __future__ import annotations

from argparse import ArgumentParser
from argparse import _ArgumentGroup

from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.internal_compat.legacy_targets import is_internal_legacy_targets_enabled


def add_internal_legacy_targets_flag(parser: ArgumentParser) -> None:
    """Expone ``--legacy-targets`` únicamente en sesiones internas."""
    if not is_internal_legacy_targets_enabled():
        return
    parser.add_argument(
        "--legacy-targets",
        action="store_true",
        help=_("Habilita rutas legacy internas para compatibilidad temporal."),
    )


def add_internal_compat_note(group: _ArgumentGroup) -> None:
    """Nota contextual para comandos que operan en modo interno."""
    if not is_internal_legacy_targets_enabled():
        return
    group.description = _("Compatibilidad internal_compat activa por feature flag interna.")
