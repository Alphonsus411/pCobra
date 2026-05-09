# QA de runtime binding para `usar numero`

## 1) Síntoma original observado en REPL

En sesiones REPL, al usar módulos Cobra con símbolos numéricos públicos (`es_finito`, `es_nan`, `signo`), el binding runtime no siempre se comportaba de forma homogénea cuando el símbolo no llegaba como descriptor de función Cobra (`dict` con `tipo="funcion"`).

Efecto práctico reportado:

- llamadas válidas desde `usar numero` podían quedar fuera del flujo esperado cuando el símbolo se resolvía como callable Python directo;
- el diagnóstico en REPL tendía a confundir “función no implementada” con “forma de binding no compatible”.

## 2) Causa raíz (estado previo)

La causa raíz histórica fue una asunción rígida en la ejecución de llamadas: el runtime esperaba primariamente funciones Cobra representadas como `dict` (`{"tipo": "funcion", ...}`), y trataba el resto como no compatible.

Ese acoplamiento hacía frágil la interoperabilidad entre:

- funciones definidas por usuario (descriptor Cobra), y
- exportaciones runtime que llegan como callables nativos de Python.

## 3) Estado actual en `src/pcobra/core/interpreter.py`

### Bloque clave: `if callable(funcion)`

En `ejecutar_llamada_funcion`, el runtime ahora contempla primero el camino de callables Python:

1. resuelve y valida argumentos (`self._verificar_valor_contexto`),
2. ejecuta `resultado = funcion(*argumentos_resueltos)`,
3. valida resultado y lo retorna,
4. y **solo después** cae al camino de función Cobra tipo `dict`.

Esto reduce el acoplamiento a un único formato de función y permite que símbolos públicos de `usar` funcionen aunque su implementación subyacente sea callable nativo.

## 4) Preservación de seguridad: saneamiento + allowlist + colisiones

El comportamiento actual mantiene barreras de seguridad en varias capas:

### 4.1 `sanitizar_exports_publicos`

Antes de inyectar símbolos en contexto, `ejecutar_usar` invoca saneamiento de exportables. Se bloquean, entre otros:

- símbolos privados/dunder,
- nombres prohibidos o no canónicos equivalentes (`append`, `map`, etc.),
- objetos de backend/módulos no exportables,
- no-callables no permitidos (excepto constantes públicas canónicas explícitas).

Si tras saneamiento no quedan símbolos exportables, se aborta con error de importación estructurado.

### 4.2 allowlist y canonicalidad de módulos

`usar` acepta únicamente alias canónicos del catálogo Cobra:

- validación contra `USAR_COBRA_ALLOWLIST`,
- validación de módulo público (`USAR_COBRA_PUBLIC_MODULES`),
- rechazo de backend directo (`pcobra.*`, rutas no públicas),
- en REPL estricto, verificación adicional de origen de archivo dentro de rutas oficiales (`corelibs`/`standard_library`).

### 4.3 política de colisiones

La inyección de símbolos es atómica en dos fases:

1. **preflight**: detección total de conflictos en el contexto activo,
2. **inyección**: solo si no hay conflictos.

Con esto se evita sobreescritura silenciosa; ante colisión se emite evento de diagnóstico y se corta la importación según política runtime.

## 5) Matriz de regresión esperada

| Caso | Entrada REPL (referencial) | Resultado esperado |
|---|---|---|
| `es_finito` | `usar numero` + `es_finito(3.14)` | Éxito, retorna booleano válido. |
| `es_nan` | `usar numero` + `es_nan(NAN)` | Éxito, retorna booleano válido. |
| `signo` | `usar numero` + `signo(-7)` | Éxito, retorna valor de signo esperado. |
| Símbolo no canónico | intento de usar/exportar alias tipo `map`/`append` | Rechazo por política de saneamiento (equivalente canónico requerido). |
| Módulo externo | `usar` sobre módulo fuera de allowlist/catálogo Cobra | Rechazo con `PermissionError` (módulo no canónico/no público/externo). |

> Nota: la tabla define expectativas de regresión funcional y de seguridad; no altera gramática del lenguaje.

## 6) No cambios en lexer/parser

Esta actualización **no requiere cambios** en el frente léxico/sintáctico. Se consideran rutas protegidas (sin modificación):

- `src/pcobra/core/lexer.py`
- `src/pcobra/core/parser.py`
- `src/pcobra/core/token_contract.py`

La variación está acotada al runtime de ejecución/inyección de símbolos en `usar` y al camino de invocación de callables en intérprete.
