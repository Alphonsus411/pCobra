"""Excepciones de dominio de la infraestructura CobraHub."""


class CobraHubError(Exception):
    """Error base producido por una operación de CobraHub."""


class PackageNotFoundError(CobraHubError):
    """El paquete solicitado no existe en el proveedor."""


class PackageIntegrityError(CobraHubError):
    """El contenido de un paquete no supera su validación de integridad."""


class PackageResolutionError(CobraHubError):
    """No se puede resolver el nombre, la versión o los metadatos solicitados."""


class PackageCompatibilityError(CobraHubError):
    """El paquete o la versión devuelta no es compatible con la solicitud."""


class PackageProviderError(CobraHubError):
    """El proveedor o transporte de paquetes no pudo completar la operación."""


__all__ = [
    "CobraHubError",
    "PackageCompatibilityError",
    "PackageIntegrityError",
    "PackageNotFoundError",
    "PackageProviderError",
    "PackageResolutionError",
]
