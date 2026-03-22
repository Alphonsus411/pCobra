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
  mientras no exista paridad real con el runtime avanzado y el SDK de referencia.
- Ningún backend fuera de `python` debe documentarse como compatibilidad total con Holobit SDK,
  compatibilidad SDK completa o equivalente semántico de soporte total.
- En todos los backends `partial`, `proyectar`, `transformar` y `graficar` deben fallar con error
  explícito y documentado; nunca pueden degradarse a no-op silencioso.

Lectura de política asociada a esta matriz:

- **Targets oficiales de transpilación**: `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`.
- **Targets con runtime oficial**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con runtime experimental/best-effort**: `go`, `java`.
- **Targets solo de transpilación sin runtime público**: `wasm`, `asm`.

Tener "runtime oficial" o "runtime experimental" **no equivale** a compatibilidad
`full` del contrato Holobit/SDK: fuera de `python`, el estado contractual
vigente sigue siendo `partial`.

Notas por backend:

- Python: hooks ejecutables y contrato `full`; `holobit-sdk` es obligatorio en instalaciones con
  Python `>=3.10`, y si aun así falta `holobit_sdk`, las primitivas avanzadas fallan explícitamente
  con `ModuleNotFoundError`.
- JavaScript, Rust, Go, cpp, Java: contrato `partial`; hooks ejecutables mínimos con error
  explícito cuando el runtime avanzado no está disponible. JavaScript no debe documentarse
  como compatibilidad real con Holobit SDK mientras solo conserve la colección de entrada y
  eleve `Error` en `proyectar`/`transformar`/`graficar`.
- WASM, ASM: contrato `partial`; hooks ejecutables mínimos que señalan error explícito en tiempo
  de ejecución/ensamblado, no no-op silencioso.
- Los hooks contractuales canónicos siguen limitados a `cobra_holobit`,
  `cobra_proyectar`, `cobra_transformar` y `cobra_graficar`; no deben aparecer
  hooks multi-backend para `escalar` o `mover`.
