# Cierre runtime filesystem posterior a #3443

## Regresión localizada

La comparación con `6ec32c48` (PR #3438) mostró que `usar_loader._aplicar_capacidades`
dejo de pasar los argumentos a `_solicitud_filesystem_confinada` y eliminó esa función.
Desde entonces, toda entrada marcada `safe_mode_decision="deny"` se rechazaba antes de
alcanzar implementaciones que sí podían operar bajo `COBRA_IO_BASE_DIR`.

La corrección no restaura esa heurística del loader: la autoridad sigue siendo
`FILESYSTEM_SYMBOL_POLICIES`/`filesystem_policy_for`, y sólo cambia una entrada a
`allow` después de que su implementación resuelva la ruta con el sandbox canónico.

## Auditoría por módulo

| Módulo / símbolos | Capacidad | Confinamiento real bajo `COBRA_IO_BASE_DIR` | `safe_mode` | Resolución |
|---|---|---|---|---|
| `archivo.leer`, `existe`, `leer_lineas` | `filesystem.read` | Sí | allow | `_resolver_ruta` |
| `archivo.escribir`, `eliminar`, `anexar` | `filesystem.write` | Sí | allow | `_resolver_ruta` |
| `temporal.archivo_temporal`, `directorio_temporal`, `limpiar` | `filesystem.write` | Sí | allow | raíz creada perezosamente y `_resolver_ruta_filesystem_confinado` |
| `datos.leer_csv`, `leer_json`, `leer_excel`, `leer_parquet`, `leer_feather` | `filesystem.read` | No; backend directo | deny | rutas arbitrarias del backend |
| `datos.escribir_csv`, `escribir_json`, `escribir_excel`, `escribir_parquet`, `escribir_feather` | `filesystem.write` | No; backend directo | deny | rutas arbitrarias del backend |
| `configuracion.leer_toml`, `leer_ini`, `leer_configuracion` | `filesystem.read` | Sí | allow | `_resolver_ruta_filesystem_confinado` |
| `ruta.existe` | `filesystem.read` | Sí | allow | `_resolver_ruta_filesystem_confinado` |
| `serializacion.leer_json`, `leer_csv` | `filesystem.read` | Sí | allow | `_resolver_ruta_filesystem_confinado` |
| `serializacion.escribir_json`, `escribir_csv` | `filesystem.write` | Sí | allow | `_resolver_ruta_filesystem_confinado` |
| `sistema.listar_dir` | `filesystem.read` | Sí | allow | `_resolver_ruta_filesystem_confinado` |

El resolver crea la raíz configurada si aún no existe, rechaza `../`, rutas absolutas
externas y cualquier symlink en los componentes intermedios o en la hoja, y valida
con `resolve(strict=False)` tanto destinos existentes como destinos todavía nuevos.
Sin `COBRA_IO_BASE_DIR`, las corelibs recién confinadas conservan su comportamiento
público previo; `safe_mode` configura una raíz explícita.
