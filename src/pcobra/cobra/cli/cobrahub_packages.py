"""Fachada compatible para paquetes CobraHub.

La lógica de repositorio vive en ``pcobra.cobra.hub.repository``. Esta clase se
mantiene como punto de entrada estable para CLI, IDLE y tests, traduciendo el
contrato independiente a los mensajes y valores booleanos históricos.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pcobra.cobra.cli.services.cobrahub_service import CobraHubProvider, CobraHubService
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra.hub.errors import (
    CobraHubError,
    PackageProviderError,
)
from pcobra.cobra.hub.repository import (
    HttpCobraHubRepository,
    PackageRepository,
    install_dir,
    json_dumps,
    package_cache_dir,
)

def listar_cache() -> list[Path]:
    """Lista los paquetes ``.co`` presentes en la caché local de CobraHub."""
    return CobraHubService().listar_cache()


def limpiar_cache(nombre: str | None = None) -> int:
    """Elimina paquetes de la caché y devuelve cuántos archivos se borraron.

    Si ``nombre`` es ``None`` se eliminan todos los ``.co`` cacheados. Si se
    indica un nombre, se borran tanto ``<nombre>.co`` como variantes
    versionadas ``<nombre>-<version>.co``.
    """
    return CobraHubService().limpiar_cache(nombre)


def validar_cache() -> list[tuple[Path, bool, str | None]]:
    """Valida cada paquete ``.co`` cacheado con los validadores de empaquetado."""
    return CobraHubService().validar_cache()


class CobraHubPackages:
    """Operaciones de paquetes publicables en CobraHub.

    Conserva la API histórica mientras delega publicación, búsqueda, descarga y
    lectura de metadatos en ``PackageRepository``. Esta separación permite sumar
    repositorios indexados, mirrors, autenticación y resolución de versiones sin
    tocar Lexer/Parser ni los comandos existentes.
    """

    def __init__(
        self,
        client: CobraHubProvider,
        repository: PackageRepository | None = None,
    ) -> None:
        self.client = client
        self.repository = repository or HttpCobraHubRepository(client)
        self.service = CobraHubService(
            client, self.repository, mostrar_error, mostrar_info
        )

    def publicar_paquete(self, ruta: str) -> bool:
        """Publica un paquete .co en CobraHub y lo guarda en caché local."""
        return self.service.publicar_paquete(ruta)

    def buscar_paquetes(self, consulta: str) -> list[dict]:
        """Busca paquetes publicados en CobraHub."""
        return self.service.buscar_paquetes(consulta)

    def instalar_paquete(
        self, nombre: str, destino: str | None = None, version: str | None = None
    ) -> bool:
        """Descarga, cachea e instala un paquete desde CobraHub."""
        return self.service.instalar_paquete(nombre, destino, version)

    def leer_metadatos(self, ruta: str | Path) -> dict[str, Any]:
        """Lee y devuelve el manifiesto/metadatos de un paquete local ``.co``."""
        try:
            return self.repository.read_metadata(ruta)
        except CobraHubError:
            raise
        except Exception as exc:
            raise PackageProviderError(str(exc)) from exc


__all__ = [
    "CobraHubPackages",
    "listar_cache",
    "limpiar_cache",
    "validar_cache",
    "install_dir",
    "json_dumps",
    "package_cache_dir",
]
