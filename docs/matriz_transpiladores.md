# Matriz de transpiladores

## Garantía mínima por backend (Tier 1 / Tier 2)

| Backend | Tier | holobit | proyectar | transformar | graficar | corelibs | standard_library |
|---|---|---|---|---|---|---|---|
| Python | Tier 1 | ✅ full | ✅ full | ✅ full | ✅ full | ✅ full | ✅ full |
| JavaScript | Tier 1 | ✅ full | ✅ full | ✅ full | ✅ full | 🟡 partial | 🟡 partial |
| Rust | Tier 1 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| WASM | Tier 1 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| Go | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| C++ | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| Java | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| ASM | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |

> `full`: soportado y cubierto por regresión. `partial`: soporte limitado/fallback. `none`: no garantizado.

## Matriz histórica de características del AST

| Característica | Python | JavaScript | C++ | Rust | Go | Java | Assembly | WASM |
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