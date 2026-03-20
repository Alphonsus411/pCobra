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
| `asm` | Tier 2 | 🟡 partial | ⚪ none | ⚪ none | ⚪ none | 🟡 partial | 🟡 partial |

> `full`: contrato de generación y hooks cubierto por regresión; si falta una dependencia opcional, el fallo debe ser explícito y documentado.
> `partial`: soporte limitado o stub explícito; genera código, pero puede terminar con error controlado en runtime.
> `none`: no garantizado y puede rechazar la generación.

## Contrato runtime Holobit

- Referencia técnica: `docs/contrato_runtime_holobit.md`.
- Hooks mínimos: `cobra_holobit`, `cobra_proyectar`, `cobra_transformar`, `cobra_graficar`.
- Inserción de hooks/imports: solo cuando el AST usa nodos Holobit.
- Política oficial ante ausencia de `holobit_sdk`: **error explícito y documentado**, no no-op silencioso.

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
