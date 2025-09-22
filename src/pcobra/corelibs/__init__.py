"""Colección de utilidades estándar para Cobra."""

from typing import Any, AsyncContextManager

from corelibs.texto import (
    mayusculas,
    minusculas,
    capitalizar,
    titulo,
    intercambiar_mayusculas,
    invertir,
    concatenar,
    quitar_espacios,
    dividir,
    dividir_derecha,
    encontrar as _texto_encontrar,
    encontrar_derecha as _texto_encontrar_derecha,
    subcadena_antes,
    subcadena_despues,
    subcadena_antes_ultima,
    subcadena_despues_ultima,
    indice as _texto_indice,
    indice_derecha as _texto_indice_derecha,
    dividir_lineas,
    unir,
    formatear as _texto_formatear,
    formatear_mapa as _texto_formatear_mapa,
    tabla_traduccion as _texto_tabla_traduccion,
    traducir as _texto_traducir,
    reemplazar,
    empieza_con,
    termina_con,
    incluye,
    quitar_prefijo,
    quitar_sufijo,
    a_snake,
    a_camel,
    quitar_envoltura,
    prefijo_comun,
    sufijo_comun,
    particionar as particionar_texto,
    particionar_derecha,
    contar_subcadena,
    indentar_texto,
    desindentar_texto,
    envolver_texto,
    acortar_texto,
    centrar_texto,
    expandir_tabulaciones,
    rellenar_ceros,
    minusculas_casefold,
    es_alfabetico,
    es_alfa_numerico,
    es_decimal,
    es_numerico,
    es_identificador,
    es_imprimible,
    es_ascii,
    es_mayusculas,
    es_minusculas,
    es_titulo,
    es_digito,
    es_espacio,
    rellenar_izquierda,
    rellenar_derecha,
    normalizar_unicode,
)

encontrar_texto = _texto_encontrar
encontrar_derecha_texto = _texto_encontrar_derecha
indice_texto = _texto_indice
indice_derecha_texto = _texto_indice_derecha
formatear_texto = _texto_formatear
formatear_texto_mapa = _texto_formatear_mapa
formatear_mapa = _texto_formatear_mapa
tabla_traduccion_texto = _texto_tabla_traduccion
tabla_traduccion = _texto_tabla_traduccion
traducir_texto = _texto_traducir
traducir = _texto_traducir
from corelibs.logica import (
    es_verdadero,
    es_falso,
    conjuncion,
    disyuncion,
    negacion,
    xor,
    nand,
    nor,
    implica,
    equivale,
    xor_multiple,
    entonces,
    si_no,
    condicional as _condicional,
    todas,
    alguna,
    ninguna,
    solo_uno,
    conteo_verdaderos,
    paridad,
)
from corelibs.numero import (
    absoluto,
    aleatorio,
    clamp,
    coeficiente_variacion,
    limitar,
    copiar_signo,
    combinaciones,
    contar_bits,
    cuartiles,
    desviacion_estandar,
    entero_a_base,
    entero_a_bytes,
    entero_desde_base,
    entero_desde_bytes,
    envolver_modular,
    es_cercano,
    es_finito,
    es_infinito,
    es_nan,
    es_par,
    es_primo,
    factorial,
    longitud_bits,
    media_armonica,
    media_geometrica,
    mcd,
    mcm,
    mediana,
    moda,
    interpolar,
    percentil,
    permutaciones,
    piso,
    potencia,
    producto,
    promedio,
    raiz,
    raiz_entera,
    rango_intercuartil,
    signo,
    rotar_bits_derecha,
    rotar_bits_izquierda,
    suma_precisa,
    redondear,
    techo,
    varianza,
    varianza_muestral,
)
from corelibs.archivo import leer, escribir, existe, eliminar
from corelibs.tiempo import ahora, formatear, dormir
from corelibs.coleccion import (
    ordenar,
    maximo,
    minimo,
    sin_duplicados,
    mapear,
    filtrar,
    reducir,
    encontrar,
    aplanar,
    agrupar_por,
    particionar,
    mezclar,
    zip_listas,
    tomar,
    tomar_mientras,
    descartar_mientras,
    scanear,
    pares_consecutivos,
)
from corelibs.seguridad import hash_sha256, generar_uuid
from corelibs.red import (
    obtener_url,
    obtener_url_async,
    enviar_post,
    enviar_post_async,
    descargar_archivo,
)
from corelibs.sistema import (
    obtener_os,
    ejecutar,
    ejecutar_async,
    ejecutar_stream,
    obtener_env,
    listar_dir,
)
from corelibs.asincrono import (
    recolectar,
    iterar_completadas,
    recolectar_resultados,
    carrera,
    primero_exitoso,
    esperar_timeout,
    reintentar_async,
    crear_tarea,
    mapear_concurrencia,
    proteger_tarea,
    ejecutar_en_hilo,
    grupo_tareas as _grupo_tareas_impl,
)


def grupo_tareas() -> AsyncContextManager[Any]:
    """Contexto asíncrono inspirado en ``asyncio.TaskGroup``.

    Reexporta :func:`pcobra.corelibs.asincrono.grupo_tareas`, garantizando un
    administrador que coordina las tareas creadas dentro del bloque y cancela
    las restantes cuando alguna falla, incluso en versiones antiguas de
    ``asyncio`` donde ``TaskGroup`` no está disponible.
    """

    return _grupo_tareas_impl()


#: Evaluador de ramas inspirado en ``when`` de Kotlin y ``case_when`` de R.
condicional = _condicional


__all__ = [
    "mayusculas",
    "minusculas",
    "capitalizar",
    "titulo",
    "intercambiar_mayusculas",
    "invertir",
    "concatenar",
    "quitar_espacios",
    "dividir",
    "dividir_derecha",
    "encontrar",
    "encontrar_texto",
    "encontrar_derecha",
    "encontrar_derecha_texto",
    "subcadena_antes",
    "subcadena_despues",
    "subcadena_antes_ultima",
    "subcadena_despues_ultima",
    "indice",
    "indice_texto",
    "indice_derecha",
    "indice_derecha_texto",
    "dividir_lineas",
    "unir",
    "formatear",
    "formatear_mapa",
    "tabla_traduccion",
    "traducir",
    "formatear_texto",
    "formatear_texto_mapa",
    "tabla_traduccion_texto",
    "traducir_texto",
    "reemplazar",
    "empieza_con",
    "termina_con",
    "incluye",
    "quitar_prefijo",
    "quitar_sufijo",
    "a_snake",
    "a_camel",
    "quitar_envoltura",
    "prefijo_comun",
    "sufijo_comun",
    "particionar_texto",
    "particionar_derecha",
    "contar_subcadena",
    "indentar_texto",
    "desindentar_texto",
    "envolver_texto",
    "acortar_texto",
    "centrar_texto",
    "expandir_tabulaciones",
    "rellenar_ceros",
    "minusculas_casefold",
    "es_alfabetico",
    "es_alfa_numerico",
    "es_decimal",
    "es_numerico",
    "es_identificador",
    "es_imprimible",
    "es_ascii",
    "es_mayusculas",
    "es_minusculas",
    "es_titulo",
    "es_digito",
    "es_espacio",
    "rellenar_izquierda",
    "rellenar_derecha",
    "normalizar_unicode",
    "es_verdadero",
    "es_falso",
    "conjuncion",
    "disyuncion",
    "negacion",
    "xor",
    "nand",
    "nor",
    "implica",
    "equivale",
    "xor_multiple",
    "entonces",
    "si_no",
    "condicional",
    "todas",
    "alguna",
    "ninguna",
    "solo_uno",
    "conteo_verdaderos",
    "paridad",
    "absoluto",
    "aleatorio",
    "clamp",
    "limitar",
    "copiar_signo",
    "combinaciones",
    "signo",
    "interpolar",
    "envolver_modular",
    "contar_bits",
    "desviacion_estandar",
    "entero_a_base",
    "entero_a_bytes",
    "entero_desde_base",
    "entero_desde_bytes",
    "es_cercano",
    "es_finito",
    "es_infinito",
    "es_nan",
    "es_par",
    "es_primo",
    "factorial",
    "longitud_bits",
    "mcd",
    "mcm",
    "mediana",
    "moda",
    "permutaciones",
    "piso",
    "potencia",
    "producto",
    "promedio",
    "raiz",
    "raiz_entera",
    "rotar_bits_derecha",
    "rotar_bits_izquierda",
    "suma_precisa",
    "redondear",
    "techo",
    "leer",
    "escribir",
    "existe",
    "eliminar",
    "ahora",
    "formatear",
    "dormir",
    "ordenar",
    "maximo",
    "minimo",
    "sin_duplicados",
    "mapear",
    "filtrar",
    "reducir",
    "encontrar",
    "aplanar",
    "agrupar_por",
    "particionar",
    "mezclar",
    "zip_listas",
    "tomar",
    "tomar_mientras",
    "descartar_mientras",
    "scanear",
    "pares_consecutivos",
    "hash_sha256",
    "generar_uuid",
    "obtener_url",
    "obtener_url_async",
    "enviar_post",
    "enviar_post_async",
    "descargar_archivo",
    "obtener_os",
    "ejecutar",
    "ejecutar_async",
    "ejecutar_stream",
    "obtener_env",
    "listar_dir",
    "recolectar",
    "iterar_completadas",
    "recolectar_resultados",
    "carrera",
    "primero_exitoso",
    "esperar_timeout",
    "reintentar_async",
    "crear_tarea",
    "mapear_concurrencia",
    "proteger_tarea",
    "ejecutar_en_hilo",
    "grupo_tareas",
]

quitar_prefijo.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.quitar_prefijo`. Equivale a ``str.removeprefix`` "
    "en Python, ``strings.TrimPrefix`` en Go y puede reproducirse en JavaScript"
    " combinando ``String.prototype.startsWith`` con ``slice``."
)

quitar_sufijo.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.quitar_sufijo`. Se inspira en ``str.removesuffix`` "
    "de Python, ``strings.TrimSuffix`` del paquete estándar de Go y en el uso de"
    " ``String.prototype.endsWith`` junto a ``slice`` en JavaScript."
)

a_snake.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.a_snake`. Convierte identificadores al estilo"
    " ``snake_case`` como hacen utilidades de JavaScript (por ejemplo, ``lodash.snakeCase``)"
    " y extensiones populares de Kotlin para homogeneizar nombres."
)

a_camel.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.a_camel`. Genera ``camelCase``/``PascalCase``"
    " emulando los transformadores presentes en Swift (``lowerCamelCase``) y en"
    " bibliotecas de JavaScript."
)

quitar_envoltura.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.quitar_envoltura`. Reproduce ``removeSurrounding``"
    " de Kotlin y puede replicarse en Swift combinando ``hasPrefix``/``hasSuffix`` con"
    " ``dropFirst``/``dropLast``, o en JavaScript mediante ``startsWith``/``endsWith`` y"
    " ``slice``."
)

dividir_lineas.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.dividir_lineas`. Ofrece la misma semántica"
    " que ``str.splitlines`` de Python, comparable a recorrer líneas con ``bufio.Scanner``"
    " en Go o dividir por expresiones ``/\r?\n/`` en JavaScript."
)

subcadena_antes.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.subcadena_antes`. Equivalente a"
    " ``substringBefore`` en Kotlin o ``substringBefore`` de Apache Commons Lang,"
    " devolviendo el prefijo previo al primer separador y permitiendo definir"
    " un valor alternativo cuando no se encuentra."
)

subcadena_despues.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.subcadena_despues`. Similar a"
    " ``substringAfter`` de Kotlin o a ``substringAfter`` de Apache Commons Lang,"
    " devuelve el segmento posterior al primer separador y acepta valores"
    " predeterminados."
)

subcadena_antes_ultima.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.subcadena_antes_ultima`. Replica el"
    " comportamiento de ``substringBeforeLast`` en Kotlin al tomar el prefijo"
    " anterior a la última coincidencia."
)

subcadena_despues_ultima.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.subcadena_despues_ultima`. Sigue la"
    " semántica de ``substringAfterLast`` en Kotlin devolviendo el segmento"
    " posterior a la última coincidencia."
)

contar_subcadena.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.contar_subcadena`. Equivale a usar"
    " ``str.count`` en Python, ``strings.Count`` en Go o dividir cadenas en JavaScript"
    " para cuantificar apariciones."
)

indentar_texto.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.indentar_texto`. Se apoya en"
    " ``textwrap.indent`` de Python para añadir prefijos de sangría y puede"
    " reproducirse en JavaScript con ``String.prototype.replace`` multilinea."
)

desindentar_texto.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.desindentar_texto`. Emplea"
    " ``textwrap.dedent`` de Python para eliminar el margen común de sangría,"
    " patrón que se replica en JavaScript calculando el prefijo compartido."
)

envolver_texto.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.envolver_texto`. Funciona como"
    " ``textwrap.wrap`` o ``textwrap.fill`` de Python permitiendo definir"
    " sangrías iniciales y posteriores al formatear párrafos."
)

acortar_texto.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.acortar_texto`. Equivale a"
    " ``textwrap.shorten`` de Python al condensar frases y añadir un marcador"
    " cuando supera el ancho indicado."
)

centrar_texto.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.centrar_texto`. Refleja ``str.center`` de"
    " Python, puede replicarse en Go combinando ``strings.Repeat`` y operaciones de"
    " concatenación y en JavaScript mediante ``padStart`` y ``padEnd``."
)

rellenar_ceros.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.rellenar_ceros`. Es análogo a ``str.zfill``"
    " de Python, a ``fmt.Sprintf(\"%0*d\", ancho, valor)`` en Go y a ``padStart``"
    " con ceros en JavaScript."
)

minusculas_casefold.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.texto.minusculas_casefold`. Sigue las reglas"
    " de ``str.casefold`` en Python, puede lograrse en Go con ``cases.Fold`` del"
    " paquete ``x/text`` y en JavaScript mediante normalización previa y"
    " ``toLocaleLowerCase``."
)

recolectar.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.asincrono.recolectar`. Equivale a"
    " coordinar varias corrutinas como haría ``Promise.all`` en JavaScript,"
    " delegando en :func:`asyncio.gather`."
)

iterar_completadas.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.asincrono.iterar_completadas`. Permite"
    " observar los resultados conforme cada tarea finaliza, similar a"
    " combinar ``Promise.race`` con iteraciones sobre ``Promise.all`` en"
    " JavaScript, aprovechando :func:`asyncio.as_completed`."
)

recolectar_resultados.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.asincrono.recolectar_resultados`. Su"
    " interfaz recuerda a ``Promise.allSettled`` al devolver el estado de"
    " cada corrutina junto al valor o la excepción capturada."
)

carrera.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.asincrono.carrera`. Expone un comportamiento"
    " semejante a ``Promise.race`` empleando :func:`asyncio.wait` para devolver"
    " el primer resultado disponible."
)

primero_exitoso.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.asincrono.primero_exitoso`. Funciona como"
    " ``Promise.any`` al devolver el primer resultado sin excepciones y agrupa"
    " los fallos restantes en una ``ExceptionGroup`` si ninguna corrutina"
    " completa con éxito."
)

mapear_concurrencia.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.asincrono.mapear_concurrencia`. Permite"
    " limitar el número de corrutinas simultáneas con ``asyncio.Semaphore``,"
    " un patrón equivalente a los *worker pools* de Go, y documenta el"
    " parámetro ``limite`` junto con la opción ``return_exceptions`` para"
    " decidir si se propagan o coleccionan los errores."
)

reintentar_async.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.asincrono.reintentar_async`. Implementa"
    " reintentos con *backoff* exponencial al estilo de utilidades basadas en"
    " ``Promise`` de JavaScript y de los bucles de reintento con gorutinas en"
    " Go, permitiendo añadir *jitter* para suavizar la contención entre"
    " clientes."
)

es_finito.__doc__ = (
    "Reexporta :func:`math.isfinite`. Indica si un número es finito tras validar"
    " que el argumento represente un real y evita confundir ``NaN`` o infinitos"
    " con valores válidos."
)

es_infinito.__doc__ = (
    "Reexporta :func:`math.isinf`. Resulta útil para detectar desbordamientos"
    " positivos o negativos antes de continuar con cálculos numéricos."
)

es_nan.__doc__ = (
    "Reexporta :func:`math.isnan`. Permite identificar ``NaN`` conforme a IEEE-754"
    " manteniendo comprobaciones de tipo explícitas."
)

signo.__doc__ = (
    "Equivalente a ``math.copysign`` combinado con ``math.sign`` de Kotlin o"
    " ``numpy.sign``. Devuelve ``-1``, ``0`` o ``1`` para enteros y preserva ceros"
    " con signo o ``NaN`` cuando se trabaja con flotantes."
)

copiar_signo.__doc__ = (
    "Reexporta :func:`math.copysign`. Replica la semántica IEEE-754 conservando"
    " ceros con signo e infinitos al combinar magnitudes y signos provenientes de"
    " diferentes cálculos."
)

interpolar.__doc__ = (
    "Interpola valores con la misma saturación que ``f32::lerp`` en Rust y"
    " documenta el paralelismo con ``kotlin.math.lerp``: el factor se acota al"
    " rango ``[0, 1]`` para evitar extrapolaciones y manejar factores fuera de"
    " rango igual que hacen dichas bibliotecas estándar."
)

envolver_modular.__doc__ = (
    "Calcula el residuo euclidiano como ``rem_euclid`` en Rust o el operador"
    " ``mod`` de Kotlin, retornando siempre un valor con el mismo signo que el"
    " divisor y proporcionando envoltura modular estable incluso con valores"
    " negativos."
)

limitar.__doc__ = (
    "Alias descriptivo de :func:`pcobra.corelibs.numero.limitar` para quienes"
    " prefieren una API en español al clamping ``min``/``max`` habitual,"
    " garantizando la propagación de ``NaN`` y validando que el mínimo no exceda"
    " al máximo."
)
