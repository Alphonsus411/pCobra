# Paridad de stdlib pública por función

Tabla publicada para usuarios finales. Se genera desde los contratos de
`src/pcobra/cobra/stdlib_contract/{core,datos,web,system}.py`.

| módulo | función | primario | python | javascript | rust | notas |
|---|---|---|---|---|---|---|
| `cobra.core` | `cobra.core.copiar_signo` | `python` | full | partial | partial | - |
| `cobra.core` | `cobra.core.es_finito` | `python` | full | partial | partial | - |
| `cobra.core` | `cobra.core.es_infinito` | `python` | full | partial | partial | - |
| `cobra.core` | `cobra.core.signo` | `python` | full | partial | partial | - |
| `cobra.datos` | `cobra.datos.a_listas` | `python` | full | partial | n/a | - |
| `cobra.datos` | `cobra.datos.de_listas` | `python` | full | partial | n/a | - |
| `cobra.datos` | `cobra.datos.filtrar` | `python` | full | partial | n/a | - |
| `cobra.datos` | `cobra.datos.seleccionar_columnas` | `python` | full | partial | n/a | - |
| `cobra.system` | `cobra.system.adjuntar` | `python` | full | partial | partial | - |
| `cobra.system` | `cobra.system.ahora` | `python` | full | partial | partial | - |
| `cobra.system` | `cobra.system.dormir` | `python` | full | partial | partial | - |
| `cobra.system` | `cobra.system.ejecutar` | `python` | full | partial | partial | - |
| `cobra.system` | `cobra.system.ejecutar_comando_async` | `python` | full | partial | partial | - |
| `cobra.system` | `cobra.system.escribir` | `python` | full | partial | partial | - |
| `cobra.system` | `cobra.system.existe` | `python` | full | partial | partial | - |
| `cobra.system` | `cobra.system.formatear` | `python` | full | partial | partial | - |
| `cobra.system` | `cobra.system.leer` | `python` | full | partial | partial | - |
| `cobra.system` | `cobra.system.listar_dir` | `python` | full | partial | partial | - |
| `cobra.system` | `cobra.system.obtener_env` | `python` | full | partial | partial | - |
| `cobra.web` | `cobra.web.descargar_archivo` | `javascript` | full | partial | n/a | JS primario partial; fallback python full |
| `cobra.web` | `cobra.web.enviar_post` | `javascript` | full | partial | n/a | JS primario partial; fallback python full |
| `cobra.web` | `cobra.web.obtener_url` | `javascript` | full | partial | n/a | JS primario partial; fallback python full |
| `cobra.web` | `cobra.web.obtener_url_texto` | `javascript` | full | partial | n/a | JS primario partial; fallback python full |

## Estado explícito de `cobra.web`

- El backend primario se mantiene en `javascript`.
- Estado del primario JS: `partial` en todas las funciones públicas declaradas.
- Funciones con fallback `python` en `full`: `cobra.web.descargar_archivo`, `cobra.web.enviar_post`, `cobra.web.obtener_url`, `cobra.web.obtener_url_texto`.

