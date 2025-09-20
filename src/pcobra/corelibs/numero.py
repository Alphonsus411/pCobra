"""Operaciones numéricas comunes."""

from __future__ import annotations

import math
import random
from typing import Any
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


def _a_float(valor: Any, nombre: str) -> float:
    """Coacciona ``valor`` a ``float`` validando que represente un número real."""

    if isinstance(valor, bool):
        valor = int(valor)
    if isinstance(valor, (int, float)):
        return float(valor)
    if isinstance(valor, (str, bytes, bytearray, memoryview)):
        raise TypeError(f"{nombre} solo acepta números reales")
    if hasattr(valor, "__float__"):
        try:
            return float(valor)
        except (TypeError, ValueError) as exc:
            raise TypeError(f"{nombre} solo acepta números reales") from exc
    raise TypeError(f"{nombre} solo acepta números reales")


def es_finito(valor) -> bool:
    """Indica si ``valor`` representa un número finito."""

    return math.isfinite(_a_float(valor, "es_finito"))


def es_infinito(valor) -> bool:
    """Indica si ``valor`` es positivo o negativo infinito."""

    return math.isinf(_a_float(valor, "es_infinito"))


def es_nan(valor) -> bool:
    """Indica si ``valor`` es ``NaN`` siguiendo la semántica IEEE-754."""

    return math.isnan(_a_float(valor, "es_nan"))


def copiar_signo(magnitud, signo):
    """Devuelve ``magnitud`` con el signo de ``signo`` conservando ``NaN`` y ceros con signo."""

    magnitud_float = _a_float(magnitud, "copiar_signo")
    signo_float = _a_float(signo, "copiar_signo")
    return math.copysign(magnitud_float, signo_float)


def signo(valor):
    """Obtiene el signo de ``valor`` preservando enteros y ceros con signo."""

    if isinstance(valor, bool):
        valor = int(valor)

    if isinstance(valor, int):
        if valor > 0:
            return 1
        if valor < 0:
            return -1
        return 0

    numero = _a_float(valor, "signo")
    if math.isnan(numero):
        return math.nan
    if numero == 0.0:
        return math.copysign(0.0, numero)
    return math.copysign(1.0, numero)


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


def _preparar_rotacion(
    valor: int, desplazamiento: int, ancho_bits: int | None
) -> tuple[int, int, int, int]:
    if not isinstance(valor, int):
        raise TypeError("La rotación de bits solo admite enteros")
    if not isinstance(desplazamiento, int):
        raise TypeError("El desplazamiento debe ser un entero")

    if ancho_bits is not None:
        if not isinstance(ancho_bits, int):
            raise TypeError("ancho_bits debe ser un entero o None")
        if ancho_bits <= 0:
            raise ValueError("ancho_bits debe ser mayor que cero")
        ancho = ancho_bits
    else:
        magnitud = abs(valor)
        ancho = max(magnitud.bit_length(), 1)

    mascara = (1 << ancho) - 1
    valor_normalizado = valor & mascara
    desplazamiento_mod = 0 if ancho == 0 else desplazamiento % ancho
    return valor_normalizado, ancho, mascara, desplazamiento_mod


def _reinterpretar_signo(resultado: int, ancho: int, ancho_bits: int | None) -> int:
    if ancho_bits is None:
        return resultado
    signo = 1 << (ancho - 1)
    if resultado & signo:
        return resultado - (1 << ancho)
    return resultado


def rotar_bits_izquierda(
    valor: int, desplazamiento: int, *, ancho_bits: int | None = None
) -> int:
    """Rota los bits de ``valor`` hacia la izquierda.

    ``desplazamiento`` se normaliza módulo la longitud efectiva del operando o el
    ``ancho_bits`` solicitado. El parámetro opcional ``ancho_bits`` permite
    emular palabras con tamaño fijo, reproduciendo la semántica de
    ``rotate_left`` en Go o Rust y devolviendo el resultado en complemento a dos
    cuando el bit más significativo queda activado.
    """

    valor_normalizado, ancho, mascara, desplazamiento_mod = _preparar_rotacion(
        valor, desplazamiento, ancho_bits
    )
    if desplazamiento_mod == 0:
        resultado = valor_normalizado
    else:
        resultado = (
            (valor_normalizado << desplazamiento_mod)
            | (valor_normalizado >> (ancho - desplazamiento_mod))
        ) & mascara
    return _reinterpretar_signo(resultado, ancho, ancho_bits)


def rotar_bits_derecha(
    valor: int, desplazamiento: int, *, ancho_bits: int | None = None
) -> int:
    """Rota los bits de ``valor`` hacia la derecha.

    Comparte la semántica de :func:`rotar_bits_izquierda`, incluyendo el soporte
    para ``ancho_bits`` como compatibilidad con ``rotate_right`` en Go o Rust.
    """

    valor_normalizado, ancho, mascara, desplazamiento_mod = _preparar_rotacion(
        valor, desplazamiento, ancho_bits
    )
    if desplazamiento_mod == 0:
        resultado = valor_normalizado
    else:
        resultado = (
            (valor_normalizado >> desplazamiento_mod)
            | (valor_normalizado << (ancho - desplazamiento_mod))
        ) & mascara
    return _reinterpretar_signo(resultado, ancho, ancho_bits)


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


def raiz_entera(valor):
    """Obtiene la raíz cuadrada entera de ``valor`` utilizando ``math.isqrt``."""

    if isinstance(valor, bool):
        valor = int(valor)
    if isinstance(valor, int):
        return math.isqrt(valor)

    numero = _a_float(valor, "raiz_entera")
    if not math.isfinite(numero) or not numero.is_integer():
        raise ValueError("raiz_entera solo acepta enteros finitos")
    return math.isqrt(int(numero))


def potencia(base, exponente):
    """Eleva ``base`` a ``exponente`` utilizando ``math.pow``."""

    return math.pow(base, exponente)


def limitar(valor, minimo, maximo):
    """Restringe ``valor`` al rango ``[minimo, maximo]`` propagando ``NaN``."""

    if isinstance(valor, bool):
        valor = int(valor)
    if isinstance(minimo, bool):
        minimo = int(minimo)
    if isinstance(maximo, bool):
        maximo = int(maximo)

    origen_entero = all(isinstance(argumento, int) for argumento in (valor, minimo, maximo))
    valor_es_int = isinstance(valor, int)
    if origen_entero:
        if minimo > maximo:
            raise ValueError("El mínimo no puede ser mayor que el máximo")
        if valor < minimo:
            return minimo
        if valor > maximo:
            return maximo
        return valor

    valor_float = _a_float(valor, "limitar")
    minimo_float = _a_float(minimo, "limitar")
    maximo_float = _a_float(maximo, "limitar")

    if math.isnan(minimo_float) or math.isnan(maximo_float):
        return math.nan
    if minimo_float > maximo_float:
        raise ValueError("El mínimo no puede ser mayor que el máximo")
    if math.isnan(valor_float):
        return math.nan

    if valor_float < minimo_float:
        resultado = minimo_float
    elif valor_float > maximo_float:
        resultado = maximo_float
    else:
        resultado = valor_float

    if valor_es_int and math.isfinite(resultado) and resultado.is_integer():
        return int(resultado)
    return resultado


def clamp(valor, minimo, maximo):
    """Restringe ``valor`` al rango ``[minimo, maximo]``."""

    return limitar(valor, minimo, maximo)


def interpolar(inicio, fin, factor):
    """Interpola linealmente de ``inicio`` a ``fin`` como ``lerp`` en Rust/Kotlin."""

    inicio_float = _a_float(inicio, "interpolar")
    fin_float = _a_float(fin, "interpolar")
    factor_float = _a_float(factor, "interpolar")

    if math.isnan(inicio_float) or math.isnan(fin_float) or math.isnan(factor_float):
        return math.nan

    if math.isinf(factor_float):
        factor_normalizado = 1.0 if factor_float > 0 else 0.0
    else:
        factor_normalizado = max(0.0, min(1.0, factor_float))

    if factor_normalizado <= 0.0:
        return inicio_float
    if factor_normalizado >= 1.0:
        return fin_float

    return inicio_float + (fin_float - inicio_float) * factor_normalizado


def envolver_modular(valor, modulo):
    """Calcula el residuo euclidiano, igual que ``rem_euclid`` o ``mod``."""

    if modulo == 0:
        raise ZeroDivisionError("El módulo no puede ser cero")

    if isinstance(valor, bool):
        valor = int(valor)
    if isinstance(modulo, bool):
        modulo = int(modulo)

    if isinstance(valor, int) and isinstance(modulo, int):
        return valor % modulo

    valor_float = _a_float(valor, "envolver_modular")
    modulo_float = _a_float(modulo, "envolver_modular")
    if modulo_float == 0.0:
        raise ZeroDivisionError("El módulo no puede ser cero")

    resultado = valor_float % modulo_float
    if resultado == 0.0:
        return math.copysign(0.0, modulo_float)
    return resultado


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


def combinaciones(n: int, k: int) -> int:
    """Retorna ``n`` sobre ``k`` usando :func:`math.comb`."""

    return math.comb(n, k)


def permutaciones(n: int, k: int | None = None) -> int:
    """Calcula las permutaciones de ``n`` tomados de ``k`` en ``k``."""

    return math.perm(n, k)


def suma_precisa(valores) -> float:
    """Suma ``valores`` con precisión extendida como :func:`math.fsum`."""

    return math.fsum(_a_float(valor, "suma_precisa") for valor in valores)
