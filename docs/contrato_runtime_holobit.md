# Contrato mínimo de runtime Holobit

## Objetivo

Definir una API mínima y estable para que los transpiladores de Cobra soporten los nodos Holobit de forma homogénea entre backends.

## Decisión explícita de producto

La decisión oficial vigente es:

- **compatibilidad total (`full`) solo en `python`**;
- **compatibilidad adaptada (`partial`) en `javascript`, `rust`, `wasm`, `go`, `cpp`, `java` y `asm`**.

En consecuencia, este documento deja de interpretar cualquier runtime adaptado como si fuera paridad funcional real con el SDK Python. Si un backend no replica el comportamiento de referencia, debe documentarse y validarse como `partial`, aunque tenga hooks ejecutables, imports concretos o adaptadores mantenidos por el proyecto.

## Nombres canónicos

El runtime Holobit mínimo expone **4 hooks contractuales**:

1. `cobra_holobit(valores)`
2. `cobra_proyectar(hb, modo)`
3. `cobra_transformar(hb, op, ...params)`
4. `cobra_graficar(hb)`

> Nota: la forma exacta de la firma varía por lenguaje destino (por ejemplo, `...params` en JavaScript/Go/Java, slices en Rust, listas en cpp), pero la **semántica debe preservarse**.

## Fuera de alcance del contrato transversal

Las funciones `escalar(hb, factor)` y `mover(hb, x, y, z)` **no forman parte del
contrato** Holobit multi-backend. Son helpers adicionales del runtime Python
(`src/pcobra/core/holobits`) y deben documentarse como tales; no deben
aparecer en la matriz contractual pública al mismo nivel que
`proyectar`/`transformar`/`graficar`.

## Contrato público serializable para `usar "holobit"`

La fachada pública `pcobra.corelibs.holobit` (consumida por `usar "holobit"`) acepta y retorna **solo** una estructura serializable JSON con este esquema:

- Tipo raíz: `object`/`dict`.
- Claves permitidas (exactas): `tipo`, `valores`.
- `tipo`: cadena exacta `"holobit"`.
- `valores`: secuencia/lista de números (`int`/`float`, no `bool`).
- No se permiten claves adicionales ni objetos/clases SDK en el contrato público.

Ejemplo válido:

```json
{"tipo":"holobit","valores":[1.0,2.0,3.0]}
```

Serialización pública:

- `serializar_holobit(hb)` produce JSON del objeto completo del contrato público.
- `deserializar_holobit(payload)` exige ese mismo contrato y rechaza payloads legacy (por ejemplo arrays sueltos o claves extra).

## Semántica mínima

### Política oficial cuando falta `holobit_sdk`

- **Política elegida**: **Opción B**, error explícito y documentado.
- En packaging, `holobit-sdk==1.0.8` forma parte de la instalación **obligatoria**
  de `pcobra` cuando se usa Python `>=3.10`.
- La ausencia efectiva de `holobit_sdk` en ese rango **no** debe producir un
  no-op silencioso en las operaciones avanzadas del runtime Holobit; se trata
  de un entorno desalineado respecto al contrato de instalación.
- **Solo `python` depende contractualmente de `holobit_sdk`** para ofrecer compatibilidad `full`.
- Los demás backends (`javascript`, `rust`, `wasm`, `go`, `cpp`, `java`, `asm`)
  **no dependen de `holobit_sdk`**: ofrecen adaptadores o puentes contractuales propios,
  y por eso siguen en `partial`.
- Cuando un backend `partial` no soporta una operación o necesita runtime externo, debe
  emitir un error o señalización explícita y verificable, nunca un no-op silencioso.
- En Python la señalización esperada es `ModuleNotFoundError` mencionando
  `holobit_sdk` y aclarando que se esperaba como dependencia obligatoria en
  Python `>=3.10`.

### `cobra_holobit(valores)`
- **Entrada**: colección indexable de valores numéricos.
- **Salida**: representación runtime del holobit para el backend.
- **Comportamiento mínimo**: si no hay tipo Holobit nativo, devolver/retener la colección de entrada.

### `cobra_proyectar(hb, modo)`
- **Entrada**: un holobit `hb` y descriptor de modo `modo`.
- **Salida**: resultado de la proyección cuando el backend la soporta.
- **Comportamiento mínimo**: delegar en implementación nativa si existe; si la
  dependencia avanzada falta o el backend no implementa proyección, fallar con
  error explícito y documentado.

### `cobra_transformar(hb, op, ...params)`
- **Entrada**: holobit `hb`, operación `op`, parámetros opcionales.
- **Salida**: holobit transformado cuando el backend soporta la operación.
- **Comportamiento mínimo**: aplicar la operación cuando el backend la soporte;
  en caso contrario, fallar con error explícito y documentado.

### `cobra_graficar(hb)`
- **Entrada**: holobit `hb`.
- **Salida**: backend-dependent (visualización o salida equivalente soportada por el backend).
- **Comportamiento mínimo**: no usar no-op silencioso; si el backend requiere
  capacidades no disponibles, fallar con error explícito y documentado.

## Política de inserción de hooks

Los transpiladores solo deben insertar hooks/imports de runtime Holobit cuando el AST incluya nodos:
- `NodoHolobit`
- `NodoProyectar`
- `NodoTransformar`
- `NodoGraficar`

Si no aparecen estos nodos, no se inyecta runtime Holobit.


## Definición contractual por backend

### Python (`full`)
- Hooks `cobra_holobit`, `cobra_proyectar`, `cobra_transformar`, `cobra_graficar`: ejecutables y alineados con el runtime Python de referencia.
- `corelibs` / `standard_library`: imports Python explícitos y símbolos invocables en el código generado.
- `holobit_sdk`: **dependencia obligatoria** para compatibilidad `full` en Python `>=3.10`.
- Error esperado si falta el SDK: `ModuleNotFoundError` mencionando `holobit_sdk`.

### JavaScript (`partial`)
- Hooks `cobra_*`: adaptador oficial mantenido por el proyecto sobre objeto runtime propio (`__cobra_tipo__ = 'holobit'`).
- `cobra_holobit`: crea la representación adaptada.
- `cobra_proyectar`: soporta `1d`, `2d`, `3d`, `vector`.
- `cobra_transformar`: soporta `escalar`, `normalizar`, `mover`/`trasladar` y `rotar` sobre eje `z`.
- `cobra_graficar`: genera vista textual y la emite por `mostrar`.
- `corelibs` / `standard_library`: alias invocables `longitud` y `mostrar` sobre capa adaptadora oficial JS.
- `holobit_sdk`: **no aplica**; el backend no lo usa.
- Limitación oficial: fuera del adaptador soportado, falla con error explícito de contrato `partial`.

### Rust (`partial`)
- Hooks `cobra_*`: adaptador oficial mantenido por el proyecto sobre `CobraHolobit`.
- `cobra_holobit`: crea `CobraHolobit`.
- `cobra_proyectar`: devuelve `Result<Vec<f64>, CobraRuntimeError>` con modos `1d`, `2d`, `3d`, `vector`.
- `cobra_transformar`: devuelve `Result<CobraHolobit, CobraRuntimeError>` con operaciones base.
- `cobra_graficar`: devuelve `Result<String, CobraRuntimeError>` y reutiliza `mostrar`.
- `corelibs` / `standard_library`: funciones inline `longitud` y `mostrar`.
- `holobit_sdk`: **no aplica**; el backend no lo usa.
- Limitación oficial: el adaptador no equivale a la semántica completa de Python y debe fallar con `CobraRuntimeError` explícito cuando no cubre una operación.

### WASM (`partial`)
- Hooks `cobra_*`: puente contractual que delega en imports host-managed `pcobra:holobit`.
- `corelibs` / `standard_library`: wrappers WAT hacia `pcobra:corelibs.longitud` y `pcobra:standard_library.mostrar`.
- `holobit_sdk`: **no aplica dentro del módulo generado**.
- Limitación oficial: la semántica final depende del host, del protocolo externo de handles y de buffers/parámetros.

### Go (`partial`)
- Hooks `cobra_*`: adaptador mínimo mantenido por el proyecto sobre `CobraHolobit`.
- `cobra_holobit`, `cobra_proyectar`, `cobra_transformar`, `cobra_graficar`: cubren la semántica básica adaptada.
- `corelibs` / `standard_library`: adaptadores mínimos `longitud` y `mostrar`.
- `holobit_sdk`: **no aplica**; el backend no lo usa.
- Limitación oficial: usa runtime best-effort no público y hace `panic` explícito cuando la operación o los datos salen del contrato adaptado.

### cpp (`partial`)
- Hooks `cobra_*`: adaptador mantenido por el proyecto sobre `CobraHolobit`.
- `cobra_holobit`, `cobra_proyectar`, `cobra_transformar`, `cobra_graficar`: cubren la semántica básica adaptada.
- `corelibs` / `standard_library`: includes verificables y adaptadores mínimos `longitud` y `mostrar`.
- `holobit_sdk`: **no aplica**; el backend no lo usa.
- Limitación oficial: usa `std::runtime_error` explícito cuando una operación sale del adaptador soportado.

### Java (`partial`)
- Hooks `cobra_*`: adaptador mantenido por el proyecto sobre `CobraHolobit`.
- `cobra_holobit`, `cobra_proyectar`, `cobra_transformar`, `cobra_graficar`: cubren la semántica básica adaptada.
- `corelibs` / `standard_library`: imports verificables y adaptadores mínimos `longitud` y `mostrar`.
- `holobit_sdk`: **no aplica**; el backend no lo usa.
- Limitación oficial: usa `UnsupportedOperationException` explícita cuando una operación sale del adaptador soportado.

### ASM (`partial`)
- Hooks `cobra_*`: capa de inspección/diagnóstico, no runtime equivalente.
- `cobra_holobit`: conserva la representación simbólica del IR.
- `cobra_proyectar`, `cobra_transformar`, `cobra_graficar`: exigen runtime externo y hacen `TRAP` explícito en el stub generado.
- `corelibs` / `standard_library`: se preservan como puntos de llamada `CALL` administrados externamente.
- `holobit_sdk`: **no aplica**; el backend no lo usa ni lo sustituye.
- Limitación oficial: no debe presentarse como backend con runtime público ni con paridad SDK equivalente.


## Mapeo de implementación runtime/hooks por backend

El cableado oficial de hooks e imports de runtime está centralizado en
`src/pcobra/cobra/transpilers/common/utils.py` (tablas `STANDARD_IMPORTS` y
`RUNTIME_HOOKS`) y cada backend `to_*.py` consume ese contrato mediante
`get_standard_imports(...)` + `get_runtime_hooks(...)`.

| Backend | Implementación hooks/imports | Punto de inyección en transpiler | Ruta mínima `corelibs`/`standard_library` |
|---|---|---|---|
| `python` | `common/utils.py` + hooks inline Python | `to_python.py` | `longitud('cobra')` y `mostrar('hola')` quedan ejecutables en salida Python. |
| `javascript` | `js_nodes/runtime_holobit.py` | `to_js.py` | Alias `longitud`/`mostrar` sobre adaptador JavaScript oficial. |
| `rust` | `rust_nodes/runtime_holobit.py` | `to_rust.py` | Helpers inline `longitud`/`mostrar` con contrato `partial`. |
| `go` | `go_nodes/runtime_holobit.py` | `to_go.py` | Adaptadores mínimos `longitud`/`mostrar` (best-effort no público). |
| `cpp` | `cpp_nodes/runtime_holobit.py` | `to_cpp.py` | Includes oficiales + adaptadores `longitud`/`mostrar`. |
| `java` | `java_nodes/runtime_holobit.py` | `to_java.py` | Imports oficiales + adaptadores `longitud`/`mostrar`. |
| `wasm` | `transpiler/wasm_runtime.py` | `to_wasm.py` | Wrappers host-managed `pcobra:corelibs.longitud` y `pcobra:standard_library.mostrar`; sin runtime oficial embebido. |
| `asm` | `asm_nodes/runtime_holobit.py` | `to_asm.py` | Puntos `CALL` preservados + fallo contractual explícito (`TRAP`) en primitivas avanzadas; backend solo de transpilación. |

## Estado de implementación por backend

La tabla contractual vigente para `holobit`, `proyectar`, `transformar`, `graficar`, `corelibs` y
`standard_library` es exactamente esta y debe mantenerse alineada con
`src/pcobra/cobra/transpilers/compatibility_matrix.py` y `docs/matriz_transpiladores.md`:

| Backend | Tier | holobit | proyectar | transformar | graficar | corelibs | standard_library |
|---|---|---|---|---|---|---|---|
| `python` | Tier 1 | ✅ full | ✅ full | ✅ full | ✅ full | ✅ full | ✅ full |
| `javascript` | Tier 1 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `rust` | Tier 1 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `wasm` | Tier 1 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `go` | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `cpp` | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `java` | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `asm` | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |

## Mapa de gaps priorizados por backend/feature (estado verificado)

| Backend | holobit | proyectar | transformar | graficar | corelibs | standard_library |
|---|---|---|---|---|---|---|
| python | sin gaps contractuales | sin gaps contractuales | sin gaps contractuales | sin gaps contractuales | sin gaps contractuales | sin gaps contractuales |
| javascript | sin paridad SDK Python completa | modos `1d/2d/3d/vector` | rotación solo eje `z` | vista textual por `mostrar` | capa adaptadora parcial | capa adaptadora parcial |
| rust | sin paridad SDK Python completa | modos `1d/2d/3d/vector` | rotación solo eje `z`; params parseados en runtime | vista textual por `mostrar` | helpers inline parciales | helpers inline parciales |
| wasm | depende de host externo | delega en host `pcobra:holobit` | delega en host `pcobra:holobit` | delega en host `pcobra:holobit` | depende de host `pcobra:corelibs` | depende de host `pcobra:standard_library` |
| go | sin paridad SDK Python completa | modos `1d/2d/3d/vector` | rotación solo eje `z` | vista textual por `mostrar` | adaptadores best-effort | adaptadores best-effort |
| cpp | sin paridad SDK Python completa | modos `1d/2d/3d/vector` | rotación solo eje `z` | vista textual por `mostrar` | adaptadores mínimos | adaptadores mínimos |
| java | sin paridad SDK Python completa | modos `1d/2d/3d/vector` | rotación solo eje `z` | vista textual por `mostrar` | adaptadores best-effort | adaptadores best-effort |
| asm | representación simbólica | requiere runtime externo (`TRAP`) | requiere runtime externo (`TRAP`) | requiere runtime externo (`TRAP`) | `CALL` externo | `CALL` externo |

- `python` es el único backend que puede figurar como `full` para estas seis features.
- `escalar` y `mover` quedan fuera de esta tabla porque son helpers del runtime Python, no features del contrato transversal.
- `javascript`, `rust`, `wasm`, `go`, `cpp`, `java` y `asm` deben permanecer en `partial`
  mientras no exista paridad real con el runtime avanzado y el SDK de referencia. En Tier 2, `cpp` es el único backend con runtime oficial fuerte; `go` y `java` quedan en codegen oficial con adaptadores mínimos; `asm` queda como backend de inspección/diagnóstico.
- Ningún backend fuera de `python` debe documentarse como compatibilidad total con Holobit SDK,
  compatibilidad SDK completa o equivalente semántico de soporte total.
- En todos los backends `partial`, `proyectar`, `transformar` y `graficar` deben fallar con error
  explícito y documentado; nunca pueden degradarse a no-op silencioso.

Lectura de política asociada a esta matriz:

> Fuente única de verdad en código: `src/pcobra/cobra/transpilers/compatibility_matrix.py`  
> (`SDK_FULL_BACKENDS`, `OFFICIAL_RUNTIME_BACKENDS`, `BEST_EFFORT_RUNTIME_BACKENDS`, `TRANSPILATION_ONLY_BACKENDS`).

- **Targets oficiales de transpilación**: `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`.
- **Targets con runtime oficial verificable**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con verificación ejecutable explícita en CLI**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con soporte oficial mantenido de `corelibs`/`standard_library` en runtime**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con adaptador Holobit mantenido por el proyecto**: `python`, `rust`, `javascript`, `cpp`.
- **Compatibilidad SDK completa**: `python`.
- **Targets con runtime best-effort no público**: `go`, `java`.
- **Targets solo de transpilación sin runtime público**: `wasm`, `asm`.

Tener "runtime oficial verificable", "runtime best-effort no público" o incluso
hooks/adaptadores generados en el código **no equivale** a compatibilidad
`full` del contrato Holobit/SDK: fuera de `python`, el estado contractual
vigente sigue siendo `partial`.

Notas por backend:

- Python: hooks ejecutables y contrato `full`; `holobit-sdk` es obligatorio en instalaciones con
  Python `>=3.10`, y si aun así falta `holobit_sdk`, las primitivas avanzadas fallan explícitamente
  con `ModuleNotFoundError`.
- JavaScript: contrato `partial`; usa un adaptador oficial mantenido por el proyecto sobre runtime JavaScript nativo. No debe documentarse como compatibilidad completa con Holobit SDK ni como backend dependiente de `holobit_sdk`.
- Rust: contrato `partial`; usa un adaptador oficial mantenido por el proyecto con `CobraHolobit`, `CobraRuntimeError` y `Result`. Implementa proyecciones y transformaciones base del adaptador, pero sin paridad total con `holobit_sdk`.
- WASM: contrato `partial`; usa hooks WAT concretos que delegan en imports host-managed (`pcobra:holobit`, `pcobra:corelibs`, `pcobra:standard_library`). No usa `holobit_sdk` dentro del módulo generado y la semántica completa sigue dependiendo del host.
- `cpp`: contrato `partial`, pero sigue siendo el backend Tier 2 con runtime oficial verificable mantenido por el proyecto mediante adaptadores mínimos ejecutables (`CobraHolobit`, `longitud`, `mostrar`, proyecciones y transformaciones base).
- `go` y `java`: contrato `partial`; se mantienen como targets oficiales de generación con adaptadores mínimos mantenidos por el proyecto, sin promesa de runtime oficial verificable ni paridad SDK.
- `asm`: contrato `partial` solo como backend de inspección/diagnóstico; conserva hooks y puntos de llamada, pero no debe presentarse como destino con runtime oficial, adaptador Holobit mantenido ni compatibilidad SDK equivalente.
- Los hooks contractuales canónicos siguen limitados a `cobra_holobit`,
  `cobra_proyectar`, `cobra_transformar` y `cobra_graficar`; no deben aparecer
  hooks multi-backend para `escalar` o `mover`.
