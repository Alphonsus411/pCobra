# Matriz de transpiladores

## Garantía mínima por backend (Tier 1 / Tier 2)

| Backend | Tier | holobit | proyectar | transformar | graficar | corelibs | standard_library |
|---|---|---|---|---|---|---|---|
| `python` | Tier 1 | ✅ full | ✅ full | ✅ full | ✅ full | ✅ full | ✅ full |
| `javascript` | Tier 1 | ✅ full | ✅ full | ✅ full | ✅ full | 🟡 partial | 🟡 partial |
| `rust` | Tier 1 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `wasm` | Tier 1 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `go` | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `cpp` | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `java` | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `asm` | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |

> `full`: contrato de generación y hooks cubierto por regresión; si falta una dependencia opcional, el fallo debe ser explícito y documentado.
> `partial`: soporte limitado o stub explícito; genera código, pero puede terminar con error controlado en runtime.
## Contrato runtime Holobit

- Referencia técnica: `docs/contrato_runtime_holobit.md`.
- Hooks mínimos: `cobra_holobit`, `cobra_proyectar`, `cobra_transformar`, `cobra_graficar`.
- Inserción de hooks/imports: solo cuando el AST usa nodos Holobit.
- Política oficial ante ausencia de `holobit_sdk`: **error explícito y documentado**, no no-op silencioso.

## Qué significa “compatibilidad con el resto de librerías”

Para `corelibs` y `standard_library`, la compatibilidad por backend se interpreta así:

- `python`: el código generado debe importar explícitamente `corelibs` y `standard_library`, y conservar llamadas a símbolos como `longitud(...)` y `mostrar(...)`.
- `javascript`: el código generado debe inyectar los imports ES module del runtime nativo (`./nativos/...`) y preservar las llamadas de símbolos.
- `rust`: el backend debe emitir `use crate::corelibs::*;` y `use crate::standard_library::*;`, dejando las llamadas como símbolos verificables en el source generado.
- `wasm`: el backend declara que el runtime se administra externamente; la compatibilidad consiste en conservar puntos de llamada WAT al runtime (`$longitud`, `$mostrar`) y no ocultar la dependencia.
- `go`: la compatibilidad mínima exige imports verificables de `cobra/corelibs` y `cobra/standard_library`, más la preservación de llamadas a símbolos.
- `cpp`: la compatibilidad mínima exige `#include <cobra/corelibs.hpp>` y `#include <cobra/standard_library.hpp>`, más la preservación de llamadas a símbolos.
- `java`: la compatibilidad mínima exige `import cobra.corelibs.*;` y `import cobra.standard_library.*;`, más la preservación de llamadas a símbolos.
- `asm`: la compatibilidad mínima consiste en declarar que el runtime externo se administra fuera del backend y preservar puntos de llamada `CALL longitud ...` / `CALL mostrar ...`.

## Estado backend por backend para Holobit

- `python`: `cobra_holobit` construye un `Holobit` real; `cobra_proyectar`, `cobra_transformar` y `cobra_graficar` delegan al runtime Python y, si falta `holobit_sdk`, fallan con `ModuleNotFoundError` explícito.
- `javascript`: `cobra_holobit` conserva la colección; `cobra_proyectar`, `cobra_transformar` y `cobra_graficar` fallan con `Error` homogéneo.
- `rust`: `cobra_holobit` devuelve la colección; `cobra_proyectar`, `cobra_transformar` y `cobra_graficar` fallan con `panic!` homogéneo.
- `wasm`: `cobra_holobit` devuelve el handle/valor i32 de entrada; `cobra_proyectar`, `cobra_transformar` y `cobra_graficar` ejecutan `unreachable` con comentario descriptivo.
- `go`: `cobra_holobit` devuelve la colección; `cobra_proyectar`, `cobra_transformar` y `cobra_graficar` fallan con `panic(fmt.Sprintf(...))` homogéneo.
- `cpp`: `cobra_holobit` devuelve la colección; `cobra_proyectar`, `cobra_transformar` y `cobra_graficar` fallan con `std::runtime_error` homogéneo.
- `java`: `cobra_holobit` devuelve la colección; `cobra_proyectar`, `cobra_transformar` y `cobra_graficar` fallan con `UnsupportedOperationException` homogéneo.
- `asm`: se mantiene como backend limitado, pero ya no usa `none` para las primitivas avanzadas; inyecta hooks `cobra_*` y las rutas de `proyectar`, `transformar` y `graficar` fallan con `TRAP` explícito y homogéneo.

## Matriz histórica de características del AST

| Característica | `python` | `javascript` | `cpp` | `rust` | `go` | `java` | `asm` | `wasm` |
|---|---|---|---|---|---|---|---|---|
| asignacion | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| assert | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| atributo | ✅ | ✅ |  |  |  |  |  |  |
| bucle_mientras | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| clase | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| condicional | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| continuar | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| decorador | ✅ | ✅ |  |  |  |  |  |  |
| defer | ✅ | ✅ |  | ✅ |  |  |  |  |
| del | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| diccionario | ✅ | ✅ |  |  |  |  |  |  |
| diccionario_comprehension | ✅ | ✅ |  |  |  |  |  |  |
| diccionario_tipo | ✅ | ✅ | ✅ |  |  |  |  |  |
| elemento |  | ✅ |  |  |  |  |  |  |
| enum | ✅ | ✅ |  |  |  |  |  |  |
| esperar | ✅ | ✅ |  |  |  |  |  |  |
| export |  | ✅ |  |  |  |  |  |  |
| for | ✅ | ✅ |  |  |  |  |  |  |
| funcion | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| garantia | ✅ | ✅ | ✅ |  |  |  |  |  |
| global | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| graficar | ✅ | ✅ |  |  |  |  |  |  |
| hilo | ✅ | ✅ |  |  |  |  |  |  |
| holobit | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| identificador | ✅ | ✅ |  |  |  |  |  |  |
| import | ✅ | ✅ |  |  |  |  |  |  |
| import_desde | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| imprimir | ✅ | ✅ |  |  |  |  |  |  |
| instancia | ✅ | ✅ |  |  |  |  |  |  |
| interface | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| lista | ✅ | ✅ |  |  |  |  |  |  |
| lista_comprehension | ✅ | ✅ |  |  |  |  |  |  |
| lista_tipo | ✅ | ✅ | ✅ |  |  |  |  |  |
| llamada_funcion | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| llamada_metodo | ✅ | ✅ |  |  |  |  |  |  |
| metodo | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| no_local | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| nolocal | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| operacion_binaria | ✅ | ✅ |  |  |  |  |  |  |
| operacion_unaria | ✅ | ✅ |  |  |  |  |  |  |
| option | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| para | ✅ | ✅ |  |  |  |  |  |  |
| pasar | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| pattern |  | ✅ | ✅ |  |  |  |  |  |
| proyectar | ✅ | ✅ |  |  |  |  |  |  |
| retorno | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| romper | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| switch | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| throw | ✅ | ✅ |  | ✅ |  |  |  |  |
| transformar | ✅ | ✅ |  |  |  |  |  |  |
| try_catch | ✅ | ✅ |  | ✅ |  |  |  |  |
| usar | ✅ |  |  |  |  |  |  |  |
| valor | ✅ | ✅ |  |  |  |  |  |  |
| with | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
| yield | ✅ | ✅ | ✅ | ✅ |  |  |  |  |
