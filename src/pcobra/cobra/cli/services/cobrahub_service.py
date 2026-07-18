"""Coordinación compartida de operaciones de paquetes CobraHub."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info
from pcobra.cobra import packaging
from pcobra.cobra.hub.errors import CobraHubError, PackageIntegrityError
from pcobra.cobra.hub.repository import PackageRepository, install_dir

logger = logging.getLogger(__name__)


class CobraHubProvider(Protocol):
    """Capacidades del proveedor HTTP requeridas por la coordinación."""

    def _validar_url(self) -> bool: ...

    def _validar_nombre_modulo(self, nombre: str) -> bool: ...


class CobraHubService:
    """Coordina publicación, búsqueda e instalación sobre un repositorio."""

    def __init__(
        self,
        provider: CobraHubProvider,
        repository: PackageRepository,
        error_handler: Callable[[str], None] = mostrar_error,
        info_handler: Callable[[str], None] = mostrar_info,
    ) -> None:
        self.provider = provider
        self.repository = repository
        self._mostrar_error = error_handler
        self._mostrar_info = info_handler

    def publicar_paquete(self, ruta: str) -> bool:
        """Publica un paquete validado en el repositorio."""
        if not self.provider._validar_url():
            return False
        try:
            if not packaging.es_paquete_cobra(ruta):
                raise PackageIntegrityError(
                    "No es un paquete Cobra: debe ser ZIP y contener cobra.pkg.json"
                )
            info = packaging.validar_paquete(ruta)
            self.repository.publish(ruta, dict(info.manifest), info.checksum)
            self._mostrar_info(_("Paquete publicado correctamente"))
            return True
        except CobraHubError as exc:
            logger.error("Error publicando paquete: %s", exc)
            self._mostrar_error(
                _("Error publicando paquete: {err}").format(err=_(str(exc)))
            )
        except Exception as exc:
            logger.error("Error publicando paquete: %s", exc)
            self._mostrar_error(
                _("Error publicando paquete: {err}").format(err=str(exc))
            )
        return False

    def buscar_paquetes(self, consulta: str) -> list[dict]:
        """Busca paquetes y adapta los resultados al contrato histórico."""
        if not self.provider._validar_url():
            return []
        try:
            return [result.as_dict() for result in self.repository.search(consulta)]
        except CobraHubError as exc:
            logger.error("Error buscando paquetes: %s", exc)
            self._mostrar_error(
                _("Error buscando paquetes: {err}").format(err=_(str(exc)))
            )
        except Exception as exc:
            logger.error("Error buscando paquetes: %s", exc)
            self._mostrar_error(
                _("Error buscando paquetes: {err}").format(err=str(exc))
            )
        return []

    def instalar_paquete(
        self, nombre: str, destino: str | None = None, version: str | None = None
    ) -> bool:
        """Descarga, valida e instala un paquete desde el repositorio."""
        cache_path: Path | None = None
        if not self.provider._validar_url():
            return False
        try:
            downloaded = self.repository.download(nombre, version)
            cache_path = downloaded.path
            if not self.provider._validar_nombre_modulo(downloaded.name):
                cache_path.unlink(missing_ok=True)
                return False
            if not packaging.es_paquete_cobra(cache_path):
                cache_path.unlink(missing_ok=True)
                raise PackageIntegrityError("La descarga no es un paquete Cobra válido")

            install_path = (
                Path(destino).expanduser()
                if destino
                else install_dir() / downloaded.name
            )
            packaging.extraer_paquete(cache_path, install_path)
            self._mostrar_info(_("Paquete instalado en {dest}").format(dest=install_path))
            return True
        except CobraHubError as exc:
            logger.error("Error instalando paquete: %s", exc)
            self._mostrar_error(
                _("Error instalando paquete: {err}").format(err=_(str(exc)))
            )
        except Exception as exc:
            logger.error("Error instalando paquete: %s", exc)
            self._mostrar_error(
                _("Error instalando paquete: {err}").format(err=str(exc))
            )
        if cache_path is not None:
            cache_path.unlink(missing_ok=True)
        return False


__all__ = ["CobraHubProvider", "CobraHubService"]
