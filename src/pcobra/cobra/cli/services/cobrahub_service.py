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
        provider: CobraHubProvider | None = None,
        repository: PackageRepository | None = None,
        error_handler: Callable[[str], None] = mostrar_error,
        info_handler: Callable[[str], None] = mostrar_info,
    ) -> None:
        self.provider = provider
        self.repository = repository
        self._mostrar_error = error_handler
        self._mostrar_info = info_handler

    def _dependencias_remotas(self) -> tuple[CobraHubProvider, PackageRepository]:
        """Devuelve las dependencias requeridas por las operaciones HTTP."""
        if self.provider is None or self.repository is None:
            raise RuntimeError(
                "Las operaciones remotas de CobraHub requieren un proveedor "
                "y un repositorio"
            )
        return self.provider, self.repository

    def publicar_paquete(self, ruta: str) -> bool:
        """Publica un paquete validado en el repositorio."""
        provider, repository = self._dependencias_remotas()
        if not provider._validar_url():
            return False
        try:
            if not packaging.es_paquete_cobra(ruta):
                raise PackageIntegrityError(
                    "No es un paquete Cobra: debe ser ZIP y contener cobra.pkg.json"
                )
            info = packaging.validar_paquete(ruta)
            repository.publish(ruta, dict(info.manifest), info.checksum)
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
        provider, repository = self._dependencias_remotas()
        if not provider._validar_url():
            return []
        try:
            return [result.as_dict() for result in repository.search(consulta)]
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
        provider, repository = self._dependencias_remotas()
        if not provider._validar_url():
            return False
        try:
            downloaded = repository.download(nombre, version)
            cache_path = downloaded.path
            if not provider._validar_nombre_modulo(downloaded.name):
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

    def listar_cache(self) -> list[Path]:
        """Lista los paquetes ``.co`` presentes en la caché local."""
        from pcobra.cobra.hub.repository import package_cache_dir

        return sorted(
            path
            for path in package_cache_dir().iterdir()
            if path.is_file() and path.suffix == ".co"
        )

    @staticmethod
    def _coincide_nombre_cache(path: Path, nombre: str) -> bool:
        """Indica si una entrada cacheada corresponde al nombre solicitado."""
        objetivo = (
            (nombre[:-3] if nombre.endswith(".co") else nombre)
            .strip()
            .lower()
            .replace(" ", "-")
        )
        return path.stem == objetivo or path.stem.startswith(f"{objetivo}-")

    def limpiar_cache(self, nombre: str | None = None) -> int:
        """Elimina paquetes cacheados y devuelve el número de borrados."""
        borrados = 0
        for path in self.listar_cache():
            if nombre is not None and not self._coincide_nombre_cache(path, nombre):
                continue
            path.unlink()
            borrados += 1
        return borrados

    def validar_cache(self) -> list[tuple[Path, bool, str | None]]:
        """Valida los paquetes cacheados con los validadores de empaquetado."""
        resultados: list[tuple[Path, bool, str | None]] = []
        for path in self.listar_cache():
            try:
                if not packaging.es_paquete_cobra(path):
                    raise PackageIntegrityError(
                        "No es un paquete Cobra: debe ser ZIP y contener cobra.pkg.json"
                    )
                packaging.validar_paquete(path)
            except CobraHubError as exc:
                resultados.append((path, False, _(str(exc))))
            except Exception as exc:
                resultados.append((path, False, str(exc)))
            else:
                resultados.append((path, True, None))
        return resultados


__all__ = ["CobraHubProvider", "CobraHubService"]
