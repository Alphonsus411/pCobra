"""Adaptador canónico de utilidades de importación."""

from ...core.import_utils import *  # noqa: F403
from ...core import import_utils as _import_utils

__all__ = [name for name in dir(_import_utils) if not name.startswith("_")]
