import hashlib
import logging
import os
import re
import urllib.parse
from pathlib import Path
from typing import Optional, Tuple, Dict, TYPE_CHECKING
from urllib.parse import urlparse

from pcobra.cobra.cli.i18n import _
from pcobra.cobra.cli.utils.messages import mostrar_error, mostrar_info

if TYPE_CHECKING:  # pragma: no cover - solo para tipado
    import requests

logger = logging.getLogger(__name__)

# URL base de CobraHub, sobreescribible en pruebas.
COBRAHUB_URL = os.environ.get("COBRAHUB_URL", "https://cobrahub.example.com/api")


class CobraHubClient:
    """Cliente para interactuar con CobraHub."""

    # Configuraciones
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    CHUNK_SIZE = 8192  # 8KB para streaming
    CONNECT_TIMEOUT = 5
    READ_TIMEOUT = 30
    MAX_RETRIES = 3
    VALID_MODULE_NAME = re.compile(r"^[\w\-\.]+$")

    def __init__(self):
        """Inicializa el cliente con configuración y sesión HTTP."""
        self.base_url = self._get_validated_base_url()
        self.session = self._configurar_sesion()

    def _get_validated_base_url(self) -> str:
        """Obtiene y valida la URL base desde variables de entorno."""
        url = os.environ.get("COBRAHUB_URL", "https://cobrahub.example.com/api")
        if len(url) > 2048:  # Límite común para URLs
            raise ValueError(_("URL de CobraHub demasiado larga"))
        return url

    def _configurar_sesion(self) -> "requests.Session":
        """Configura una sesión HTTP con reintentos y timeouts."""
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3 import Retry
        except ModuleNotFoundError as exc:  # pragma: no cover - error de entorno
            raise RuntimeError(
                _("El comando requiere el paquete 'requests'. Instálalo para continuar.")) from exc

        session = requests.Session()
        retry_strategy = Retry(
            total=self.MAX_RETRIES,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        return session

    def _validar_url(self) -> bool:
        """Verifica que la URL de CobraHub sea segura."""
        try:
            parsed = urlparse(self.base_url)
            if not parsed.scheme == "https":
                mostrar_error(_("COBRAHUB_URL debe usar HTTPS (https://)"))
                return False

            if not parsed.hostname:
                mostrar_error(_("URL de CobraHub inválida"))
                return False

            allowed = os.environ.get("COBRA_HOST_WHITELIST", "")
            if allowed:
                hosts = {h.strip().lower() for h in allowed.split(",") if h.strip()}
                hostname_normalizado = parsed.hostname.lower()
                if hostname_normalizado not in hosts:
                    mostrar_error(_("Host de CobraHub no permitido"))
                    return False

            return True
        except Exception as e:
            logger.error(f"Error validando URL: {e}")
            mostrar_error(_("URL de CobraHub inválida"))
            return False

    def _validar_ruta_destino(self, destino: str) -> Optional[str]:
        """Valida y retorna la ruta absoluta de destino si es válida."""
        try:
            ruta = Path(destino)
            if ruta.is_absolute() or ".." in ruta.parts:
                mostrar_error(_("Ruta de destino inválida"))
                return None

            ruta_abs = ruta.resolve()
            dir_trabajo = Path.cwd().resolve()

            try:
                ruta_abs.relative_to(dir_trabajo)
            except ValueError:
                mostrar_error(_("Ruta fuera del directorio de trabajo"))
                return None

            if not os.access(ruta_abs.parent, os.W_OK):
                mostrar_error(_("Sin permisos de escritura en el destino"))
                return None

            return str(ruta_abs)
        except Exception as e:
            logger.error(f"Error validando ruta: {e}")
            mostrar_error(_("Error validando ruta de destino"))
            return None

    def _validar_nombre_modulo(self, nombre: str) -> bool:
        """Valida el formato del nombre del módulo."""
        if not self.VALID_MODULE_NAME.match(nombre):
            mostrar_error(_("Nombre de módulo inválido"))
            return False
        return True

    def _calcular_checksum(self, ruta: str) -> Optional[str]:
        """Calcula el checksum SHA-256 de un archivo."""
        try:
            sha256 = hashlib.sha256()
            with open(ruta, "rb") as f:
                for chunk in iter(lambda: f.read(self.CHUNK_SIZE), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculando checksum: {e}")
            mostrar_error(_("Error calculando checksum: {err}").format(err=str(e)))
            return None

    def _verificar_tamaño_archivo(self, ruta: str) -> bool:
        """Verifica que el archivo no exceda el tamaño máximo."""
        try:
            if os.path.getsize(ruta) > self.MAX_FILE_SIZE:
                mostrar_error(_("Archivo demasiado grande"))
                return False
            return True
        except Exception as e:
            logger.error(f"Error verificando tamaño: {e}")
            return False

    def publicar_modulo(self, ruta: str) -> bool:
        """Publica un archivo .co en CobraHub."""
        if not self._validar_url():
            return False

        if not os.path.exists(ruta):
            mostrar_error(_("No se encontró el módulo {path}").format(path=ruta))
            return False

        if not self._verificar_tamaño_archivo(ruta):
            return False

        checksum = self._calcular_checksum(ruta)
        if not checksum:
            return False

        try:
            with open(ruta, "rb") as f:
                headers = {
                    "X-Content-Checksum": checksum,
                    "Idempotency-Key": checksum,
                }
                with self.session.post(
                    f"{self.base_url}/modulos",
                    files={"file": f},
                    headers=headers,
                    timeout=(self.CONNECT_TIMEOUT, self.READ_TIMEOUT),
                ) as response:
                    response.raise_for_status()

            mostrar_info(_("Módulo publicado correctamente"))
            return True
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 409:
                mostrar_info(_("Módulo ya existía en CobraHub"))
                return True
            logger.error(f"Error publicando módulo: {e}")
            mostrar_error(
                _("Error publicando módulo: {err}").format(err=str(e))
            )
            return False
        except Exception as e:
            logger.error(f"Error publicando módulo: {e}")
            mostrar_error(_("Error publicando módulo: {err}").format(err=str(e)))
            return False

    def descargar_modulo(self, nombre: str, destino: str) -> bool:
        """Descarga un módulo de CobraHub asegurando HTTPS y hosts autorizados."""
        if not self._validar_nombre_modulo(nombre):
            return False

        destino_abs = self._validar_ruta_destino(destino)
        if not destino_abs or not self._validar_url():
            return False

        try:
            with self.session.get(
                f"{self.base_url}/modulos/{urllib.parse.quote(nombre)}",
                timeout=(self.CONNECT_TIMEOUT, self.READ_TIMEOUT),
                stream=True,
            ) as response:
                response.raise_for_status()

                final_url = response.url or ""
                if not final_url.lower().startswith("https://"):
                    response.close()
                    raise ValueError(
                        _("La descarga fue redirigida a una URL insegura")
                    )

                parsed_final = urlparse(final_url)
                allowed_hosts = set()

                base_host = urlparse(self.base_url).hostname
                if base_host:
                    allowed_hosts.add(base_host.lower())

                allowed = os.environ.get("COBRA_HOST_WHITELIST", "")
                if allowed:
                    allowed_hosts.update(
                        host.strip().lower()
                        for host in allowed.split(",")
                        if host.strip()
                    )

                final_host = parsed_final.hostname.lower() if parsed_final.hostname else None
                if not final_host or final_host not in allowed_hosts:
                    response.close()
                    raise ValueError(
                        _("La descarga fue redirigida a un host no permitido")
                    )

                tamaño_total = 0
                checksum_servidor = response.headers.get("X-Content-Checksum")
                sha256 = hashlib.sha256()

                with open(destino_abs, "wb") as f:
                    for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                        tamaño_total += len(chunk)
                        if tamaño_total > self.MAX_FILE_SIZE:
                            f.close()
                            os.unlink(destino_abs)
                            mostrar_error(_("Archivo descargado demasiado grande"))
                            return False
                        sha256.update(chunk)
                        f.write(chunk)

                if checksum_servidor and sha256.hexdigest() != checksum_servidor:
                    os.unlink(destino_abs)
                    mostrar_error(_("Verificación de integridad fallida"))
                    return False

            mostrar_info(_("Módulo descargado en {dest}").format(dest=destino_abs))
            return True
        except Exception as e:
            logger.error(f"Error descargando módulo: {e}")
            mostrar_error(_("Error descargando módulo: {err}").format(err=str(e)))
            if destino_abs and os.path.exists(destino_abs):
                try:
                    os.unlink(destino_abs)
                except Exception:
                    pass
            return False


# Funciones conveniencia para interacción sencilla con CobraHub.
def publicar_modulo(ruta: str) -> bool:
    """Publica un módulo en CobraHub."""
    os.environ["COBRAHUB_URL"] = COBRAHUB_URL
    return CobraHubClient().publicar_modulo(ruta)


def descargar_modulo(nombre: str, destino: str) -> bool:
    """Descarga un módulo desde CobraHub con redirecciones HTTPS y autorizadas."""
    os.environ["COBRAHUB_URL"] = COBRAHUB_URL
    return CobraHubClient().descargar_modulo(nombre, destino)


__all__ = ["CobraHubClient", "publicar_modulo", "descargar_modulo"]

