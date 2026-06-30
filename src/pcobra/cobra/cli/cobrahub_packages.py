"""Fachada compatible para paquetes CobraHub.

La lógica de repositorio vive en ``pcobra.cobra.hub.repository``. Esta clase se
mantiene como punto de entrada estable para CLI, IDLE y tests, traduciendo el
contrato independiente a los mensajes y valores booleanos históricos.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pcobra.cobra.cli.i18n import _
from pcobra.cobra.hub.repository import (
    HttpCobraHubRepository,
    PackageRepository,
    install_dir,
    json_dumps,
    package_cache_dir,
)

if TYPE_CHECKING:  # pragma: no cover - solo para tipado
    from pcobra.cobra.cli.cobrahub_client import CobraHubClient

logger = logging.getLogger(__name__)


def _mostrar_error(mensaje: str) -> None:
    """Emite errores vía la fachada legacy para conservar mocks existentes."""
    from pcobra.cobra.cli import cobrahub_client

    cobrahub_client.mostrar_error(mensaje)


def _mostrar_info(mensaje: str) -> None:
    """Emite información vía la fachada legacy para conservar mocks existentes."""
    from pcobra.cobra.cli import cobrahub_client

    cobrahub_client.mostrar_info(mensaje)


class CobraHubPackages:
    """Operaciones de paquetes publicables en CobraHub.

    Conserva la API histórica mientras delega publicación, búsqueda, descarga y
    lectura de metadatos en ``PackageRepository``. Esta separación permite sumar
    repositorios indexados, mirrors, autenticación y resolución de versiones sin
    tocar Lexer/Parser ni los comandos existentes.
    """

    def __init__(
        self,
        client: "CobraHubClient",
        repository: PackageRepository | None = None,
    ) -> None:
        self.client = client
        self.repository = repository or HttpCobraHubRepository(client)

    def publicar_paquete(self, ruta: str) -> bool:
        """Publica un paquete .co en CobraHub y lo guarda en caché local."""
        from pcobra.cobra.packaging import es_paquete_cobra, validar_paquete

        if not self.client._validar_url():
            return False
        try:
            if not es_paquete_cobra(ruta):
                raise ValueError(
                    "No es un paquete Cobra: debe ser ZIP y contener cobra.pkg.json"
                )
            info = validar_paquete(ruta)
            self.repository.publish(ruta, dict(info.manifest), info.checksum)
            _mostrar_info(_("Paquete publicado correctamente"))
            return True
        except Exception as e:
            logger.error(f"Error publicando paquete: {e}")
            _mostrar_error(_("Error publicando paquete: {err}").format(err=str(e)))
            return False

    def buscar_paquetes(self, consulta: str) -> list[dict]:
        """Busca paquetes publicados en CobraHub."""
        if not self.client._validar_url():
            return []
        try:
            return [result.as_dict() for result in self.repository.search(consulta)]
        except Exception as e:
            logger.error(f"Error buscando paquetes: {e}")
            _mostrar_error(_("Error buscando paquetes: {err}").format(err=str(e)))
            return []

    def instalar_paquete(
        self, nombre: str, destino: str | None = None, version: str | None = None
    ) -> bool:
        """Descarga, cachea e instala un paquete desde CobraHub."""
        from pcobra.cobra.packaging import (
            es_paquete_cobra,
            extraer_paquete,
            normalizar_nombre_paquete,
            validar_version_paquete,
        )

        cache_path: Path | None = None
        try:
            normalized_name = normalizar_nombre_paquete(nombre)
            normalized_version = (
                validar_version_paquete(version) if version is not None else None
            )
        except ValueError as e:
            _mostrar_error(str(e))
            return False
        if (
            not self.client._validar_nombre_modulo(normalized_name)
            or not self.client._validar_url()
        ):
            return False
        try:
            downloaded = self.repository.download(normalized_name, normalized_version)
            cache_path = downloaded.path

            if not es_paquete_cobra(cache_path):
                os.unlink(cache_path)
                _mostrar_error(_("La descarga no es un paquete Cobra válido"))
                return False

            install_path = (
                Path(destino).expanduser()
                if destino
                else install_dir() / normalized_name
            )
            extraer_paquete(cache_path, install_path)
            _mostrar_info(_("Paquete instalado en {dest}").format(dest=install_path))
            return True
        except Exception as e:
            logger.error(f"Error instalando paquete: {e}")
            _mostrar_error(_("Error instalando paquete: {err}").format(err=str(e)))
            if cache_path is not None and cache_path.exists():
                try:
                    os.unlink(cache_path)
                except Exception:
                    pass
            return False

    def leer_metadatos(self, ruta: str | Path) -> dict[str, Any]:
        """Lee y devuelve el manifiesto/metadatos de un paquete local ``.co``."""
        return self.repository.read_metadata(ruta)


__all__ = [
    "CobraHubPackages",
    "install_dir",
    "json_dumps",
    "package_cache_dir",
]
