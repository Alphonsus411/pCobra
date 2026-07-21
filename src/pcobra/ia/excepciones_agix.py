"""Excepciones estables del adaptador oficial de AGIX."""


class DependenciaAGIXNoDisponibleError(ImportError):
    """Indica que la dependencia opcional AGIX no está disponible."""


class FalloMotorAGIXError(RuntimeError):
    """Indica que AGIX rechazó una invocación válida del analizador."""


class RespuestaAGIXInvalidaError(ValueError):
    """Indica que AGIX devolvió una respuesta incompatible con su contrato."""
