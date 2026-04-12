from pathlib import Path
from typing import Iterable, Optional, Union

from pcobra.cobra.cli.i18n import _


def validar_archivo_existente(ruta: str | Path) -> Path:
    """Valida que un archivo exista.

    Args:
        ruta: Ruta al archivo a comprobar.

    Returns:
        Path: Objeto Path de la ruta validada.

    Raises:
        FileNotFoundError: Si el archivo no existe.
    """
    input_path = Path(ruta).expanduser()
    absolute_path = Path.cwd() / input_path
    resolved_path = absolute_path.resolve(strict=False)

    if not resolved_path.exists() or not resolved_path.is_file():
        raise FileNotFoundError(
            _(
                "El archivo no existe o no es un archivo regular. "
                "Ruta original: '{original}', ruta resuelta: '{resolved}'"
            ).format(original=ruta, resolved=resolved_path)
        )
    return resolved_path


ExtraValidatorsInput = Union[str, Path, Iterable[Union[str, Path]]]


def _convertir_path_a_str(valor: Union[str, Path]) -> str:
    if isinstance(valor, Path):
        return str(valor)
    if isinstance(valor, str):
        return valor
    raise TypeError("Los validadores extra deben ser rutas o listas de rutas")


def normalizar_validadores_extra(
    extra_validators: Optional[ExtraValidatorsInput],
) -> Optional[Union[str, list[str]]]:
    """Normaliza las rutas de validadores extra en un formato soportado."""

    if extra_validators is None:
        return None

    if isinstance(extra_validators, (str, Path)):
        return _convertir_path_a_str(extra_validators)

    if isinstance(extra_validators, Iterable):
        normalizados: list[str] = []
        for elemento in extra_validators:
            normalizados.append(_convertir_path_a_str(elemento))
        return normalizados

    raise TypeError("Los validadores extra deben ser rutas o listas de rutas")
