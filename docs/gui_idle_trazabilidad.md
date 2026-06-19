# Matriz de trazabilidad del IDLE gráfico

Esta matriz documenta únicamente comportamiento existente en el IDLE gráfico canónico (`pcobra.gui.idle.main`) y sus utilidades compartidas de `pcobra.gui.runtime`. No marca como disponible ninguna capacidad que dependa de trabajo futuro: cuando una acción depende de una opción o dependencia externa, el estado lo indica explícitamente.

| Funcionalidad visible | Archivo de implementación | Función/handler | Dependencia Lexer/Parser | Documentación relacionada | Estado |
| --- | --- | --- | --- | --- | --- |
| Nuevo | `src/pcobra/gui/idle.py` / `src/pcobra/gui/runtime.py` | `nuevo_handler` → `crear_archivo_nuevo_en_editor()` → `nuevo_archivo()` | No usa Lexer/Parser; solo reinicia `GuiFileState` y el contenido del editor. | `docs/LIBRO_PROGRAMACION_COBRA.md`, sección 10.1, “Gestión de archivos / Nuevo”. | Implementado. |
| Abrir | `src/pcobra/gui/idle.py` / `src/pcobra/gui/runtime.py` | `abrir_handler` → `cargar_archivo()` → `abrir_archivo_desde_ruta()` / `cargar_archivo_desde_arbol()` | No usa Lexer/Parser; valida ruta/sandbox y, desde el árbol, extensión Cobra antes de leer. | `docs/LIBRO_PROGRAMACION_COBRA.md`, sección 10.1, “Gestión de archivos / Abrir” y “Árbol de directorios”. | Implementado. |
| Guardar | `src/pcobra/gui/idle.py` / `src/pcobra/gui/runtime.py` | `guardar_handler` → `guardar_archivo_activo()` → `guardar_archivo_en_estado()` | No usa Lexer/Parser; escribe el contenido normalizado del editor tras validar la ruta activa. | `docs/LIBRO_PROGRAMACION_COBRA.md`, sección 10.1, “Gestión de archivos / Guardar”. | Implementado. |
| Guardar como | `src/pcobra/gui/idle.py` / `src/pcobra/gui/runtime.py` | `guardar_como_handler` → `guardar_en()` → `guardar_archivo_como()` | No usa Lexer/Parser; escribe en una ruta nueva validada por la política de sandbox. | `docs/LIBRO_PROGRAMACION_COBRA.md`, sección 10.1, “Gestión de archivos / Guardar como”. | Implementado. |
| Recargar | `src/pcobra/gui/idle.py` / `src/pcobra/gui/runtime.py` | `recargar_handler` → `recargar_archivo_activo()` | No usa Lexer/Parser; vuelve a leer desde disco el archivo activo. | `docs/LIBRO_PROGRAMACION_COBRA.md`, sección 10.1, “Gestión de archivos / Recargar”. | Implementado. |
| Árbol de directorios / Establecer raíz | `src/pcobra/gui/idle.py` / `src/pcobra/gui/runtime.py` | `establecer_raiz_arbol_handler()` → `normalizar_ruta_archivo_gui()` → `reconstruir_arbol()` / `cargar_archivo_desde_evento_arbol()` → `crear_arbol_directorios()` / `listar_directorio_cobra()` | No usa Lexer/Parser; normaliza la raíz contra el sandbox, exige que sea directorio, filtra carpetas y archivos `.co`/`.cobra`, y delega la carga a los handlers de archivo. | `docs/LIBRO_PROGRAMACION_COBRA.md`, sección 10.1, “Gestión de archivos / Árbol de directorios”. | Implementado. |
| Ejecutar | `src/pcobra/gui/idle.py` / `src/pcobra/gui/runtime.py` | `crear_handler_ejecucion()` → `ejecutar_o_transpilar()` → `ejecutar_codigo()` | Sí. `ejecutar_codigo()` llama a `analizar_codigo()`, que ejecuta `Lexer(codigo).tokenizar()` y `Parser(tokens).parsear()` antes de `InterpretadorCobra().ejecutar_ast(ast)`. | `docs/LIBRO_PROGRAMACION_COBRA.md`, sección 10.1, “Ejecución y transpilación / Ejecutar”. | Implementado. |
| Transpilar | `src/pcobra/gui/idle.py` / `src/pcobra/gui/runtime.py` | Switch `activar` + `crear_handler_ejecucion()` → `ejecutar_o_transpilar()` → `transpilar_codigo()` | Sí. `transpilar_codigo()` llama a `analizar_codigo()` y entrega el AST al transpilador seleccionado si existe en `TRANSPILERS`. | `docs/LIBRO_PROGRAMACION_COBRA.md`, sección 10.1, “Ejecución y transpilación”. | Implementado para targets disponibles en el registro público de transpiladores. |
| Tokens | `src/pcobra/gui/idle.py` / `src/pcobra/gui/runtime.py` | `tokens_handler` generado por `crear_handler_tokens()` → `mostrar_tokens()` | Sí. `mostrar_tokens()` usa `analizar_codigo()`; muestra los tokens obtenidos del Lexer y propaga errores léxicos/sintácticos formateados. | `docs/LIBRO_PROGRAMACION_COBRA.md`, sección 10.1, “Inspección del lenguaje / Tokens”. | Implementado. |
| AST | `src/pcobra/gui/idle.py` / `src/pcobra/gui/runtime.py` | `ast_handler` generado por `crear_handler_ast()` → `mostrar_ast()` | Sí. `mostrar_ast()` usa `analizar_codigo()`; muestra la representación serializada del AST generado por Parser. | `docs/LIBRO_PROGRAMACION_COBRA.md`, sección 10.1, “Inspección del lenguaje / AST”. | Implementado. |
| Sugerencias del Libro | `src/pcobra/gui/idle.py` / `src/pcobra/gui/runtime.py` | `crear_boton_sugerencias_libro()` + `sugerencias_handler` generado por `crear_handler_sugerencias()` → `generar_reporte_sugerencias()` | Sí, dependencia exacta: `generar_reporte_sugerencias()` llama primero a `analizar_codigo()`, que ejecuta `Lexer(codigo).tokenizar()` y después `Parser(tokens).parsear()`. Si falla Lexer o Parser, la salida visible empieza por `Errores léxicos/sintácticos:` y no llama al motor IA; si ambos pasan, muestra `No se detectaron errores...` y agrupa `Sugerencias del Libro` en `Léxico/sintaxis`, `Estilo`, `Nombres`, `Forma canónica` y `Observabilidad`. | `docs/LIBRO_PROGRAMACION_COBRA.md`, sección 10.1, “Sugerencias de código / Sugerencias del Libro”. | Implementado mediante dependencia opcional: el botón/flujo existe, pero las sugerencias solo están disponibles cuando el motor opcional está instalado; sin esa dependencia se informa que la acción está deshabilitada tras la validación Lexer/Parser. La entrada canónica para crear este handler es `crear_handler_sugerencias`; los alias internos de compatibilidad no forman parte de la API recomendada. |


## Especificación normativa

La especificación consolidada de acciones soportadas, funciones runtime, validación previa con `Lexer`/`Parser` y restricción del selector de transpilación a `python`, `javascript` y `rust` está en [`docs/gui_idle_especificacion.md`](gui_idle_especificacion.md).

## Auditoría CI de reglas derivadas del Libro

El flujo de trazabilidad de **Sugerencias del Libro** se protege con el script
`scripts/ci/audit_reglas_libro_programacion.py`. Este script lee de forma
estática `src/pcobra/ia/reglas_libro_programacion.py`, extrae los campos `id`,
`seccion` y `fragmento_valido` de cada entrada de `REGLAS_LIBRO_PROGRAMACION` y
falla si detecta cualquiera de estas condiciones:

1. Una regla no declara un `id`, una `seccion` o un `fragmento_valido` literal y
   no vacío.
2. La `seccion` no usa el formato trazable `§N[.N] Título`.
3. La sección referenciada no existe como encabezado en
   `docs/LIBRO_PROGRAMACION_COBRA.md`, lo que evita reglas huérfanas respecto al
   Libro.
4. El `fragmento_valido` deja de parsear con el `Lexer` y el `Parser` oficiales
   de Cobra.

Para ejecutar la auditoría de forma aislada:

```bash
python scripts/ci/audit_reglas_libro_programacion.py
```

La prueba `tests/unit/test_audit_reglas_libro_programacion.py` invoca la misma
función de auditoría para que el contrato también forme parte de la suite de
`pytest`.
