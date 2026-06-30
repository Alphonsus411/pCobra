"""API de paquetes CobraHub.

Esta capa concentra la lógica específica de paquetes ``.co``: publicación,
búsqueda, instalación, caché local y lectura de metadatos. Recibe un
``CobraHubClient`` compatible para reutilizar la configuración HTTP, validación
de URL y límites comunes sin mezclar el flujo legacy de módulos.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import urllib.parse
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pcobra.cobra.cli.i18n import _

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
    """Operaciones de paquetes publicables en CobraHub."""

    def __init__(self, client: "CobraHubClient") -> None:
        self.client = client

    def publicar_paquete(self, ruta: str) -> bool:
        """Publica un paquete .co en CobraHub y lo guarda en caché local."""
        from pcobra.cobra.packaging import validar_paquete

        if not self.client._validar_url():
            return False
        try:
            info = validar_paquete(ruta)
            checksum = info.checksum
            with open(ruta, "rb") as f:
                with self.client.session.post(
                    f"{self.client.base_url}/paquetes",
                    files={"file": f},
                    data={"metadata": json_dumps(info.manifest)},
                    headers={
                        "X-Content-Checksum": checksum,
                        "Idempotency-Key": checksum,
                    },
                    timeout=(
                        self.client.CONNECT_TIMEOUT,
                        self.client.READ_TIMEOUT,
                    ),
                ) as response:
                    response.raise_for_status()
            cache_path = package_cache_dir() / Path(ruta).name
            if Path(ruta).resolve() != cache_path.resolve():
                shutil.copy2(ruta, cache_path)
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
            with self.client.session.get(
                f"{self.client.base_url}/paquetes",
                params={"q": consulta},
                timeout=(self.client.CONNECT_TIMEOUT, self.client.READ_TIMEOUT),
            ) as response:
                response.raise_for_status()
                data = response.json() if hasattr(response, "json") else []
            if isinstance(data, dict):
                return list(data.get("results", []))
            return list(data)
        except Exception as e:
            logger.error(f"Error buscando paquetes: {e}")
            _mostrar_error(_("Error buscando paquetes: {err}").format(err=str(e)))
            return []

    def instalar_paquete(self, nombre: str, destino: str | None = None) -> bool:
        """Descarga, cachea e instala un paquete desde CobraHub."""
        from pcobra.cobra.packaging import extraer_paquete

        if not self.client._validar_nombre_modulo(nombre) or not self.client._validar_url():
            return False
        cache_path = package_cache_dir() / f"{nombre}.co"
        try:
            with self.client.session.get(
                f"{self.client.base_url}/paquetes/{urllib.parse.quote(nombre)}",
                timeout=(self.client.CONNECT_TIMEOUT, self.client.READ_TIMEOUT),
                stream=True,
            ) as response:
                response.raise_for_status()
                checksum_servidor = response.headers.get("X-Content-Checksum")
                sha256 = hashlib.sha256()
                tamaño_total = 0

                with open(cache_path, "wb") as out:
                    for chunk in response.iter_content(chunk_size=self.client.CHUNK_SIZE):
                        if not chunk:
                            continue
                        tamaño_total += len(chunk)
                        if tamaño_total > self.client.MAX_FILE_SIZE:
                            out.close()
                            os.unlink(cache_path)
                            _mostrar_error(_("Archivo descargado demasiado grande"))
                            return False
                        sha256.update(chunk)
                        out.write(chunk)

            if checksum_servidor and sha256.hexdigest() != checksum_servidor:
                os.unlink(cache_path)
                _mostrar_error(_("Verificación de integridad fallida"))
                return False

            install_path = Path(destino).expanduser() if destino else install_dir() / nombre
            extraer_paquete(cache_path, install_path)
            _mostrar_info(_("Paquete instalado en {dest}").format(dest=install_path))
            return True
        except Exception as e:
            logger.error(f"Error instalando paquete: {e}")
            _mostrar_error(_("Error instalando paquete: {err}").format(err=str(e)))
            if cache_path.exists():
                try:
                    os.unlink(cache_path)
                except Exception:
                    pass
            return False

    def leer_metadatos(self, ruta: str | Path) -> dict[str, Any]:
        """Lee y devuelve el manifiesto/metadatos de un paquete local ``.co``."""
        from pcobra.cobra.packaging import validar_paquete

        info = validar_paquete(ruta)
        return dict(info.manifest)


def package_cache_dir() -> Path:
    """Devuelve el directorio de caché local para paquetes CobraHub."""
    cache = Path(
        os.environ.get(
            "COBRAHUB_CACHE_DIR", str(Path.home() / ".cobra" / "hub" / "cache")
        )
    ).expanduser()
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def install_dir() -> Path:
    """Devuelve el directorio de instalación por defecto para paquetes."""
    dest = Path(
        os.environ.get("COBRAHUB_INSTALL_DIR", str(Path.home() / ".cobra" / "packages"))
    ).expanduser()
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def json_dumps(value: Any) -> str:
    """Serializa metadatos de paquete de forma estable."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


__all__ = [
    "CobraHubPackages",
    "install_dir",
    "json_dumps",
    "package_cache_dir",
]
