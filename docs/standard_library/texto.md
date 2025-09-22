# Utilidades de texto de la biblioteca estándar

La biblioteca `standard_library.texto` se apoya en `pcobra.corelibs.texto` para ofrecer funciones de alto nivel centradas en limpieza y comparación de cadenas.

## `quitar_acentos(texto: str) -> str`
Elimina marcas diacríticas conservando los caracteres base. Es útil para normalizar entradas de usuarios antes de comparar o indexar.

```python
from standard_library.texto import quitar_acentos
assert quitar_acentos("pingüino") == "pinguino"
```

## `normalizar_espacios(texto: str) -> str`
Colapsa cualquier secuencia de espacios, tabulaciones o saltos de línea en un único espacio y elimina los extremos.

```python
from standard_library.texto import normalizar_espacios
assert normalizar_espacios("  hola\t mundo \n") == "hola mundo"
```

## `es_palindromo(texto: str, *, ignorar_espacios=True, ignorar_tildes=True, ignorar_mayusculas=True) -> bool`
Comprueba si una cadena se lee igual al derecho y al revés aplicando las reglas indicadas. Permite ignorar espacios, mayúsculas y acentos.

```python
from standard_library.texto import es_palindromo
assert es_palindromo("Sé verlas al revés") is True
assert es_palindromo("áa", ignorar_tildes=False) is False
```

## `es_anagrama(texto: str, otro: str, *, ignorar_espacios=True) -> bool`
Determina si dos textos contienen las mismas letras (tras eliminar acentos y, por defecto, espacios). Es ideal para juegos de palabras o validaciones.

```python
from standard_library.texto import es_anagrama
assert es_anagrama("Roma", "amor") is True
assert es_anagrama("cosa", "caso ", ignorar_espacios=False) is False
```

## Búsquedas con `encontrar`/`indice`
`encontrar` y `encontrar_derecha` replican la semántica de `str.find`/`str.rfind` devolviendo `-1` cuando no hallan la subcadena, o bien el valor indicado en `por_defecto`. Las variantes `indice` e `indice_derecha` siguen a `str.index`/`str.rindex` y permiten retornar un valor alternativo en lugar de lanzar un error. Los índices que se devuelven son base cero, en sintonía con Python y JavaScript.

```python
from standard_library.texto import encontrar, indice

assert encontrar("banana", "na") == 2
assert encontrar("banana", "zz", por_defecto=None) is None
assert indice("banana", "zz", por_defecto=-1) == -1
```

## Formateo con `formatear` y `formatear_mapa`
`formatear` ofrece interpolación posicional inspirada en `str.format`, mientras que `formatear_mapa` acepta diccionarios o `Mapping` para resolver marcadores con nombre, igual que `str.format_map`.

```python
from standard_library.texto import formatear, formatear_mapa

assert formatear("{} {}", "hola", "cobra") == "hola cobra"
assert formatear_mapa("Hola {nombre}", {"nombre": "Cobra"}) == "Hola Cobra"
```

## Traducciones con `tabla_traduccion` y `traducir`
`tabla_traduccion` construye tablas compatibles con `str.maketrans`, ya sea a partir de mapeos o de cadenas de origen/destino y caracteres a eliminar. `traducir` aplica la tabla resultante emulando `str.translate` tanto en Python como en JavaScript.

```python
from standard_library.texto import tabla_traduccion, traducir

tabla = tabla_traduccion("áé", "ae", "í")
assert traducir("áéí", tabla) == "ae"
```

Todas estas funciones respetan Unicode y aprovechan los normalizadores base disponibles en Cobra y en los lenguajes de destino.
