"""Adaptador canónico de errores bajo ``pcobra.cobra.core``."""

from ...core.errors import *  # noqa: F403
from ...core import errors as _errors

__all__ = [name for name in dir(_errors) if not name.startswith("_")]
