"""Operaciones numéricas comunes."""

from __future__ import annotations

import math
import random
from statistics import StatisticsError, median, mode, pstdev, stdev

_ALFABETO_DEFECTO = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def absoluto(valor):
    """Devuelve el valor absoluto de ``valor`` preservando el tipo de enteros."""

    resultado = math.fabs(valor)
    if isinstance(valor, int) and resultado.is_integer():
        return int(resultado)
    return resultado


def redondear(valor, ndigitos: int | None = None):
    """Redondea ``valor`` a ``ndigitos`` cifras decimales."""

    if ndigitos is None:
        return round(valor)
    return round(valor, ndigitos)


def piso(valor):
    """Equivalente a ``math.floor``."""

    return math.floor(valor)


def techo(valor):
    """Equivalente a ``math.ceil``."""

    return math.ceil(valor)


def mcd(*valores: int) -> int:
    """Calcula el máximo común divisor de uno o más enteros."""

    if not valores:
        raise TypeError("mcd requiere al menos un argumento")
    return math.gcd(*valores)


def mcm(*valores: int) -> int:
    """Calcula el mínimo común múltiplo de uno o más enteros."""

    if not valores:
        raise TypeError("mcm requiere al menos un argumento")
    return math.lcm(*valores)


def es_cercano(
    a,
    b,
    *,
    tolerancia_relativa: float = 1e-09,
    tolerancia_absoluta: float = 0.0,
) -> bool:
    """Compara ``a`` y ``b`` usando tolerancias relativas y absolutas.

    Los parámetros ``tolerancia_relativa`` y ``tolerancia_absoluta`` permiten
    ajustar la sensibilidad de la comparación, igual que :func:`math.isclose`.
    """

    return math.isclose(a, b, rel_tol=tolerancia_relativa, abs_tol=tolerancia_absoluta)


def producto(valores, inicio=1):
    """Obtiene el producto acumulado de ``valores`` iniciando en ``inicio``.

    El argumento opcional ``inicio`` define el factor neutro inicial, tal como
    ``start`` en :func:`math.prod`.
    """

    return math.prod(valores, start=inicio)


def _validar_base(base: int) -> None:
    if not isinstance(base, int):
        raise TypeError("La base debe ser un entero")
    if base < 2 or base > 36:
        raise ValueError("La base debe estar entre 2 y 36")


def entero_a_base(valor: int, base: int, *, alfabeto: str | None = None) -> str:
    """Convierte ``valor`` a una cadena en la ``base`` indicada.

    El parámetro opcional ``alfabeto`` permite proporcionar los símbolos a usar
    para los dígitos, siempre que cubran la base solicitada.
    """

    if not isinstance(valor, int):
        raise TypeError("Solo se admiten enteros para la conversión de base")
    _validar_base(base)
    tabla = alfabeto or _ALFABETO_DEFECTO
    if len(tabla) < base:
        raise ValueError("El alfabeto proporcionado es demasiado corto para la base")
    if len(set(tabla[:base])) != base:
        raise ValueError("El alfabeto debe contener símbolos únicos para la base")

    if valor == 0:
        return tabla[0]

    signo = "-" if valor < 0 else ""
    valor = abs(valor)
    digitos: list[str] = []
    while valor > 0:
        valor, resto = divmod(valor, base)
        digitos.append(tabla[resto])
    return signo + "".join(reversed(digitos))


def entero_desde_base(cadena: str, base: int, *, alfabeto: str | None = None) -> int:
    """Convierte ``cadena`` escrita en ``base`` a un entero decimal.

    Se puede personalizar el conjunto de símbolos mediante ``alfabeto`` para que
    coincida con el utilizado en :func:`entero_a_base`.
    """

    if not isinstance(cadena, str):
        raise TypeError("La representación debe ser una cadena de texto")
    _validar_base(base)
    cadena = cadena.strip()
    if not cadena:
        raise ValueError("La cadena no puede estar vacía")

    tabla = alfabeto or _ALFABETO_DEFECTO
    if len(tabla) < base:
        raise ValueError("El alfabeto proporcionado es demasiado corto para la base")
    if len(set(tabla[:base])) != base:
        raise ValueError("El alfabeto debe contener símbolos únicos para la base")

    signo = 1
    if cadena[0] in "+-":
        if len(cadena) == 1:
            raise ValueError("La cadena no contiene dígitos")
        signo = -1 if cadena[0] == "-" else 1
        cadena = cadena[1:]

    if not cadena:
        raise ValueError("La cadena no contiene dígitos")

    if alfabeto is None:
        mapa = {car: indice for indice, car in enumerate(tabla[:base])}
        mapa.update({car.lower(): indice for indice, car in enumerate(tabla[:base])})
    else:
        mapa = {car: indice for indice, car in enumerate(tabla[:base])}

    valor = 0
    for caracter in cadena:
        if caracter not in mapa or mapa[caracter] >= base:
            raise ValueError(f"Dígito '{caracter}' inválido para la base {base}")
        valor = valor * base + mapa[caracter]
    return signo * valor


def longitud_bits(valor: int) -> int:
    """Devuelve la cantidad de bits necesarios para representar ``valor``.

    La semántica coincide con :meth:`int.bit_length`, por lo que los enteros
    negativos utilizan su magnitud absoluta para el cálculo y ``0`` retorna
    ``0``.
    """

    if not isinstance(valor, int):
        raise TypeError("longitud_bits solo acepta valores enteros")
    return valor.bit_length()


def contar_bits(valor: int) -> int:
    """Cuenta cuántos bits a ``1`` contiene la representación de ``valor``.

    Esta función es equivalente a :meth:`int.bit_count` y funciona tanto para
    enteros positivos como negativos usando complemento a dos.
    """

    if not isinstance(valor, int):
        raise TypeError("contar_bits solo acepta valores enteros")
    return valor.bit_count()


def entero_a_bytes(
    valor: int,
    longitud: int | None = None,
    *,
    byteorder: str = "big",
    signed: bool = False,
) -> bytes:
    """Convierte ``valor`` en una secuencia de bytes.

    Si ``longitud`` es ``None`` se calculará automáticamente el mínimo número
    de bytes capaz de representar el entero respetando ``signed``. El parámetro
    ``byteorder`` debe ser ``"big"`` o ``"little"``, coherente con
    :meth:`int.to_bytes`.
    """

    if not isinstance(valor, int):
        raise TypeError("Solo se pueden convertir valores enteros a bytes")
    if not isinstance(byteorder, str):
        raise TypeError("byteorder debe ser una cadena de texto")
    if byteorder not in {"big", "little"}:
        raise ValueError("byteorder debe ser 'big' o 'little'")

    if longitud is not None:
        if not isinstance(longitud, int):
            raise TypeError("La longitud debe ser un entero")
        if longitud < 0:
            raise ValueError("La longitud no puede ser negativa")
        return valor.to_bytes(longitud, byteorder, signed=signed)

    if valor < 0 and not signed:
        raise OverflowError("Se requiere signed=True para convertir enteros negativos")

    longitud_calculada = 1
    while True:
        try:
            return valor.to_bytes(longitud_calculada, byteorder, signed=signed)
        except OverflowError:
            longitud_calculada += 1


def entero_desde_bytes(
    datos,
    *,
    byteorder: str = "big",
    signed: bool = False,
) -> int:
    """Construye un entero a partir de ``datos`` interpretados como bytes.

    ``datos`` puede ser cualquier objeto similar a bytes. El parámetro
    ``byteorder`` acepta los mismos valores que :func:`entero_a_bytes`.
    """

    if not isinstance(byteorder, str):
        raise TypeError("byteorder debe ser una cadena de texto")
    if byteorder not in {"big", "little"}:
        raise ValueError("byteorder debe ser 'big' o 'little'")

    try:
        buffer = bytes(datos)
    except TypeError as exc:  # pragma: no cover - error explícito
        raise TypeError("Se requiere un objeto similar a bytes") from exc

    return int.from_bytes(buffer, byteorder, signed=signed)


def raiz(valor, indice: float = 2):
    """Calcula la raíz ``indice``-ésima de ``valor``."""

    indice_float = float(indice)
    if indice_float == 0:
        raise ValueError("El índice de la raíz no puede ser cero")
    if valor < 0:
        if indice_float.is_integer():
            if int(indice_float) % 2 == 0:
                raise ValueError(
                    "No se puede calcular la raíz par de un número negativo"
                )
        else:
            raise ValueError(
                "No se puede calcular la raíz de índice fraccionario de un número negativo"
            )
    magnitud = math.pow(abs(valor), 1.0 / indice_float)
    return -magnitud if valor < 0 else magnitud


def potencia(base, exponente):
    """Eleva ``base`` a ``exponente`` utilizando ``math.pow``."""

    return math.pow(base, exponente)


def clamp(valor, minimo, maximo):
    """Restringe ``valor`` al rango ``[minimo, maximo]``."""

    if minimo > maximo:
        raise ValueError("El mínimo no puede ser mayor que el máximo")
    return max(min(valor, maximo), minimo)


def aleatorio(inicio: float = 0.0, fin: float = 1.0, semilla: int | None = None) -> float:
    """Genera un número aleatorio uniforme entre ``inicio`` y ``fin``."""

    if inicio > fin:
        raise ValueError("El inicio no puede ser mayor que el fin")
    if semilla is not None:
        generador = random.Random(semilla)
        return generador.uniform(inicio, fin)
    return random.uniform(inicio, fin)


def mediana(valores) -> float:
    """Calcula la mediana de ``valores`` usando :mod:`statistics`."""

    if not valores:
        raise ValueError("No se puede calcular la mediana de una secuencia vacía")
    return median(valores)


def moda(valores):
    """Calcula la moda de ``valores`` usando :mod:`statistics`."""

    if not valores:
        raise ValueError("No se puede calcular la moda de una secuencia vacía")
    try:
        return mode(valores)
    except StatisticsError as exc:  # pragma: no cover - comportamiento defensivo
        raise ValueError(str(exc)) from exc


def desviacion_estandar(valores, *, muestral: bool = False) -> float:
    """Obtiene la desviación estándar de ``valores``."""

    if not valores:
        raise ValueError("No se puede calcular la desviación estándar de una secuencia vacía")
    funcion = stdev if muestral else pstdev
    try:
        return funcion(valores)
    except StatisticsError as exc:  # pragma: no cover - comportamiento defensivo
        raise ValueError(str(exc)) from exc


def es_par(n: int) -> bool:
    """Retorna ``True`` si *n* es par."""
    return n % 2 == 0


def es_primo(n: int) -> bool:
    """Determina si *n* es un número primo."""
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def factorial(n: int) -> int:
    """Calcula el factorial de *n*."""
    resultado = 1
    for i in range(1, n + 1):
        resultado *= i
    return resultado


def promedio(valores) -> float:
    """Calcula el promedio de una secuencia de valores."""
    return sum(valores) / len(valores) if valores else 0.0
