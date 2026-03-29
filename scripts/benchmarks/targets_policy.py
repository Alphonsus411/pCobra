"""Compatibilidad para scripts de benchmarks.

Este módulo conserva la ruta histórica `scripts.benchmarks.targets_policy`
reexportando la implementación canónica ubicada dentro del paquete instalable.
"""

from pcobra.cobra.benchmarks.targets_policy import *  # noqa: F403
