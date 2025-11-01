from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Optional, TypeVar, Union

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
    path = Path(ruta)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(
            _("El archivo '{path}' no existe").format(path=path)
        )
    return path


ExtraValidatorsInput = Union[str, Path, Iterable[Union[str, Path]]]

ValidatorT = TypeVar("ValidatorT")


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


def cargar_validadores_extra(
    extra_validators: Optional[Union[str, Path, Iterable[Union[str, Path]]]],
    loader: Callable[[str], Iterable[ValidatorT]],
) -> Optional[Union[Iterable[ValidatorT], list[ValidatorT]]]:
    """Convierte rutas de validadores en instancias utilizando ``loader``.

    Args:
        extra_validators: Rutas o colecciones de rutas a módulos de validadores.
        loader: Función encargada de cargar los validadores para una ruta.

    Returns:
        Lista de validadores cargados o el valor original si ya eran instancias.
    """

    if extra_validators is None:
        return None

    if isinstance(extra_validators, (str, Path)):
        return loader(_convertir_path_a_str(extra_validators))

    if isinstance(extra_validators, Iterable):
        elementos = list(extra_validators)
        if all(isinstance(elemento, (str, Path)) for elemento in elementos):
            cargados: list[ValidatorT] = []
            for elemento in elementos:
                resultado = loader(_convertir_path_a_str(elemento))
                if isinstance(resultado, Iterable) and not isinstance(resultado, (str, bytes)):
                    cargados.extend(resultado)
                elif resultado is not None:
                    cargados.append(resultado)
            return cargados

        return elementos

    return extra_validators
