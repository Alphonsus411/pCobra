# Contrato mínimo de runtime Holobit

## Objetivo

Definir una API mínima y estable para que los transpiladores de Cobra soporten los nodos Holobit de forma homogénea entre backends.

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

## Semántica mínima

### Política oficial cuando falta `holobit_sdk`

- **Política elegida**: **Opción B**, error explícito y documentado.
- En packaging, `holobit-sdk==1.0.8` forma parte de la instalación **obligatoria**
  de `pcobra` cuando se usa Python `>=3.10`.
- La ausencia efectiva de `holobit_sdk` en ese rango **no** debe producir un
  no-op silencioso en las operaciones avanzadas del runtime Holobit; se trata
  de un entorno desalineado respecto al contrato de instalación.
- Cuando el backend depende de `holobit_sdk` para ejecutar `proyectar`,
  `transformar` o `graficar`, debe emitir una excepción/runtime error
  descriptivo que identifique la dependencia faltante.
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


## Compatibilidad real por backend Tier 1 parcial

### JavaScript
- `holobit`: representación propia inmutable (`{ __cobra_tipo__: 'holobit', valores, historial }`).
- `proyectar`: soporta `1d`, `2d`, `3d`, `vector`.
- `transformar`: soporta `escalar`, `normalizar`, `mover`/`trasladar` y `rotar` sobre eje `z`.
- `graficar`: genera una vista textual `Holobit(...)` y la emite vía `mostrar`.
- `corelibs` / `standard_library`: alias invocables `longitud` y `mostrar` sobre una capa adaptadora oficial JS.
- Sigue en `partial` porque no replica el SDK Python completo ni sus capacidades avanzadas.

### Rust
- `holobit`: `struct CobraHolobit { valores, historial }`.
- `proyectar`: devuelve `Result<Vec<f64>, CobraRuntimeError>` con modos `1d`, `2d`, `3d`, `vector`.
- `transformar`: devuelve `Result<CobraHolobit, CobraRuntimeError>` con operaciones base (`escalar`, `normalizar`, `mover`, `rotar` planar).
- `graficar`: devuelve `Result<String, CobraRuntimeError>` y reutiliza `mostrar`.
- `corelibs` / `standard_library`: funciones inline `longitud` y `mostrar` mantenidas por el proyecto.
- Sigue en `partial` porque no existe paridad semántica completa con `holobit_sdk` ni con el runtime Python.

### WASM
- `holobit`, `proyectar`, `transformar`, `graficar`: wrappers WAT concretos que delegan en imports host-managed `pcobra:holobit`.
- `corelibs` / `standard_library`: wrappers WAT concretos hacia `pcobra:corelibs.longitud` y `pcobra:standard_library.mostrar`.
- El backend deja de depender de `unreachable` como fallback principal.
- Sigue en `partial` porque el comportamiento final depende del runtime host y del protocolo externo de handles/parámetros.

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

- `python` es el único backend que puede figurar como `full` para estas seis features.
- `escalar` y `mover` quedan fuera de esta tabla porque son helpers del runtime Python, no features del contrato transversal.
- `javascript`, `rust`, `wasm`, `go`, `cpp`, `java` y `asm` deben permanecer en `partial`
  mientras no exista paridad real con el runtime avanzado y el SDK de referencia. En Tier 2, `cpp` es el único backend con runtime oficial fuerte; `go` y `java` quedan en codegen oficial con adaptadores mínimos; `asm` queda como backend de inspección/diagnóstico.
- Ningún backend fuera de `python` debe documentarse como compatibilidad total con Holobit SDK,
  compatibilidad SDK completa o equivalente semántico de soporte total.
- En todos los backends `partial`, `proyectar`, `transformar` y `graficar` deben fallar con error
  explícito y documentado; nunca pueden degradarse a no-op silencioso.

Lectura de política asociada a esta matriz:

- **Targets oficiales de transpilación**: `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`.
- **Targets con runtime oficial verificable**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con verificación ejecutable explícita en CLI**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con soporte oficial mantenido de `corelibs`/`standard_library` en runtime**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con soporte Holobit avanzado mantenido por el proyecto**: `python`, `rust`, `javascript`, `cpp`.
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
- JavaScript: contrato `partial`; usa un adaptador oficial mantenido por el proyecto sobre runtime javascript nativo. `cobra_holobit` crea un objeto runtime propio, `proyectar` soporta salidas 1D/2D/3D/vector, `transformar` cubre `escalar`, `normalizar`, `mover`/`trasladar` y rotación planar sobre `z`, y `graficar` produce una vista textual. No debe documentarse como compatibilidad completa con Holobit SDK.
- Rust: contrato `partial`; usa un adaptador oficial mantenido por el proyecto con `CobraHolobit`, `CobraRuntimeError` y `Result`. Implementa proyecciones y transformaciones base equivalentes al adaptador oficial, pero sin paridad total con `holobit_sdk`.
- WASM: contrato `partial`; usa hooks WAT concretos que delegan en imports host-managed (`pcobra:holobit`, `pcobra:corelibs`, `pcobra:standard_library`). Ya no usa `unreachable`, pero la semántica completa sigue dependiendo del host.
- `cpp`: contrato `partial`, pero sigue siendo el backend Tier 2 con runtime oficial verificable mantenido por el proyecto mediante adaptadores mínimos ejecutables (`CobraHolobit`, `longitud`, `mostrar`, proyecciones y transformaciones base).
- `go` y `java`: contrato `partial`; se mantienen como targets oficiales de generación con adaptadores mínimos mantenidos por el proyecto, sin promesa de runtime oficial verificable ni paridad SDK.
- `asm`: contrato `partial` solo como backend de inspección/diagnóstico; conserva hooks y puntos de llamada, pero no debe presentarse como destino con runtime oficial, soporte Holobit avanzado mantenido ni compatibilidad SDK equivalente.
- Los hooks contractuales canónicos siguen limitados a `cobra_holobit`,
  `cobra_proyectar`, `cobra_transformar` y `cobra_graficar`; no deben aparecer
  hooks multi-backend para `escalar` o `mover`.
