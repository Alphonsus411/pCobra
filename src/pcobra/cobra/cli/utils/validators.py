from pathlib import Path

from cobra.cli.i18n import _


def validar_archivo_existente(ruta: str | Path) -> Path:
    """Valida que un archivo exista.

    Args:
        ruta: Ruta al archivo a comprobar.

    Returns:
        Path: Objeto Path de la ruta validada.

    Raises:
        FileNotFoundError: Si el archivo no existe.
    """
    path = Path(ruta)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(
            _("El archivo '{path}' no existe").format(path=path)
        )
    return path
