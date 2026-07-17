"""Adaptador compatible de la caché compartida de CobraHub."""

from pcobra.cobra.hub.cache import (
    COBRA_INSTALLER_CACHE_DIR_ENV,
    CobraInstallerCache,
    CobraInstallerCacheEntry,
    installer_cache_dir,
)

__all__ = [
    "COBRA_INSTALLER_CACHE_DIR_ENV",
    "CobraInstallerCache",
    "CobraInstallerCacheEntry",
    "installer_cache_dir",
]
