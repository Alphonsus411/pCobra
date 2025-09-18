"""Colección de utilidades estándar para Cobra."""

from corelibs.texto import (
    mayusculas,
    minusculas,
    capitalizar,
    titulo,
    invertir,
    concatenar,
    quitar_espacios,
    dividir,
    dividir_derecha,
    subcadena_antes,
    subcadena_despues,
    subcadena_antes_ultima,
    subcadena_despues_ultima,
    dividir_lineas,
    unir,
    reemplazar,
    empieza_con,
    termina_con,
    incluye,
    quitar_prefijo,
    quitar_sufijo,
    particionar as particionar_texto,
    particionar_derecha,
    contar_subcadena,
    centrar_texto,
    rellenar_ceros,
    minusculas_casefold,
    rellenar_izquierda,
    rellenar_derecha,
    normalizar_unicode,
)
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
    contar_bits,
    desviacion_estandar,
    entero_a_base,
    entero_a_bytes,
    entero_desde_base,
    entero_desde_bytes,
    es_cercano,
    es_par,
    es_primo,
    factorial,
    longitud_bits,
    mcd,
    mcm,
    mediana,
    moda,
    piso,
    potencia,
    producto,
    promedio,
    raiz,
    rotar_bits_derecha,
    rotar_bits_izquierda,
    redondear,
    techo,
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
    carrera,
    esperar_timeout,
    crear_tarea,
)

__all__ = [
    "mayusculas",
    "minusculas",
    "capitalizar",
    "titulo",
    "invertir",
    "concatenar",
    "quitar_espacios",
    "dividir",
    "dividir_derecha",
    "subcadena_antes",
    "subcadena_despues",
    "subcadena_antes_ultima",
    "subcadena_despues_ultima",
    "dividir_lineas",
    "unir",
    "reemplazar",
    "empieza_con",
    "termina_con",
    "incluye",
    "quitar_prefijo",
    "quitar_sufijo",
    "particionar_texto",
    "particionar_derecha",
    "contar_subcadena",
    "centrar_texto",
    "rellenar_ceros",
    "minusculas_casefold",
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
    "todas",
    "alguna",
    "ninguna",
    "solo_uno",
    "conteo_verdaderos",
    "paridad",
    "absoluto",
    "aleatorio",
    "clamp",
    "contar_bits",
    "desviacion_estandar",
    "entero_a_base",
    "entero_a_bytes",
    "entero_desde_base",
    "entero_desde_bytes",
    "es_cercano",
    "es_par",
    "es_primo",
    "factorial",
    "longitud_bits",
    "mcd",
    "mcm",
    "mediana",
    "moda",
    "piso",
    "potencia",
    "producto",
    "promedio",
    "raiz",
    "rotar_bits_derecha",
    "rotar_bits_izquierda",
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
    "carrera",
    "esperar_timeout",
    "crear_tarea",
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

carrera.__doc__ = (
    "Reexporta :func:`pcobra.corelibs.asincrono.carrera`. Expone un comportamiento"
    " semejante a ``Promise.race`` empleando :func:`asyncio.wait` para devolver"
    " el primer resultado disponible."
)
