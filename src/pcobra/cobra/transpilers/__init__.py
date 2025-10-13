"""Facilita el acceso a los distintos transpiladores de Cobra."""

from typing import TYPE_CHECKING, Any

from pcobra.cobra.transpilers.common.utils import BaseTranspiler

if TYPE_CHECKING:  # pragma: no cover - solo para análisis estático
    from pcobra.cobra.transpilers.reverse.base import BaseReverseTranspiler


def __getattr__(name: str) -> Any:  # pragma: no cover - importación diferida
    if name == "BaseReverseTranspiler":
        from pcobra.cobra.transpilers.reverse.base import BaseReverseTranspiler

        return BaseReverseTranspiler
    raise AttributeError(name)


__all__ = ["BaseTranspiler", "BaseReverseTranspiler"]

