# Especificación del IDLE gráfico (`pcobra.gui.idle`)

Esta especificación describe las acciones visibles soportadas por `src/pcobra/gui/idle.py` y su función runtime correspondiente en `src/pcobra/gui/runtime.py`. El IDLE debe mantener esta tabla alineada con la matriz de trazabilidad en [`docs/gui_idle_trazabilidad.md`](gui_idle_trazabilidad.md).

## Contrato general

- La interfaz principal se construye en `pcobra.gui.idle.main` y delega la lógica reusable en `pcobra.gui.runtime`.
- Las acciones que analizan código Cobra deben ejecutar primero el flujo canónico `Lexer(codigo).tokenizar()` y después `Parser(tokens).parsear()` mediante `analizar_codigo()` antes de interpretar, transpilar, mostrar tokens, mostrar AST o solicitar sugerencias.
- La acción **Sugerencias del Libro** debe pasar siempre primero por `Lexer` y `Parser`. Si alguno falla, el IDLE debe mostrar los errores léxicos/sintácticos y no debe invocar el motor opcional de sugerencias.
- El motor IA canónico para sugerencias es `agix`; `agi-core` no debe usarse como sustituto ni dependencia paralela sin una ADR nueva. La decisión vigente está documentada en [`docs/ADR/002-motor-ia-sugerencias-agix.md`](ADR/002-motor-ia-sugerencias-agix.md).
- El selector de transpilación del IDLE solo puede mostrar los targets públicos canónicos: `python`, `javascript` y `rust`. No debe exponer aliases, targets legacy ni backends experimentales.
- La gestión del árbol de archivos es funcionalidad de archivos/rutas de la GUI: no afecta la sintaxis Cobra y no debe requerir cambios en `Lexer` ni `Parser`.

## Acciones soportadas y funciones runtime

| Acción visible en `idle.py` | Handler o flujo en `idle.py` | Función runtime correspondiente | Requisito Lexer/Parser | Comportamiento esperado |
| --- | --- | --- | --- | --- |
| Nuevo | `nuevo_handler` | `crear_archivo_nuevo_en_editor()` → `nuevo_archivo()` | No aplica. | Limpia el editor, reinicia `GuiFileState`, marca el archivo como nuevo sin ruta y actualiza la salida con un mensaje de creación en memoria. |
| Abrir | `abrir_handler` → `cargar_archivo()` | `abrir_archivo_desde_ruta()` → `cargar_archivo_en_estado()` | No aplica. | Lee una ruta validada por el sandbox GUI, carga el contenido en el editor, actualiza `GuiFileState` y reconstruye el árbol. |
| Guardar | `guardar_handler` | `guardar_archivo_activo()` → `guardar_archivo_en_estado()` | No aplica. | Si hay ruta activa, guarda el contenido normalizado del editor en esa ruta y limpia la marca de cambios sin guardar; si no hay ruta, deriva a Guardar como. |
| Guardar como | `guardar_como_handler` → `guardar_en()` | `guardar_archivo_como()` → `guardar_archivo_en_estado()` | No aplica. | Guarda el contenido normalizado del editor en la ruta indicada, actualiza la ruta activa y reconstruye el árbol. |
| Recargar | `recargar_handler` | `recargar_archivo_activo()` → `abrir_archivo_desde_ruta()` | No aplica. | Vuelve a leer desde disco el archivo activo, reemplaza el contenido del editor y limpia la marca de cambios. |
| Ejecutar | `ejecutar_handler`, creado por `crear_handler_ejecucion()` | `ejecutar_o_transpilar()` → `ejecutar_codigo()` | Obligatorio. | Normaliza el texto del editor, ejecuta `analizar_codigo()` (`Lexer` y `Parser`) y entrega el AST a `InterpretadorCobra().ejecutar_ast(ast)`, capturando stdout/stderr. |
| Transpilar desde Ejecutar | Selector + switch `activar` + `ejecutar_handler` | `ejecutar_o_transpilar()` → `transpilar_codigo()` | Obligatorio. | Cuando el switch de transpilación está activo, valida que el target seleccionado exista en `TRANSPILERS`, analiza con `Lexer`/`Parser` y genera código desde el AST. El selector solo puede contener `python`, `javascript` y `rust`. |
| Tokens | `tokens_handler`, creado por `crear_handler_tokens()` | `mostrar_tokens()` → `analizar_codigo()` | Obligatorio. | Ejecuta `Lexer` y `Parser` mediante `analizar_codigo()` y muestra una línea por token. Los errores se formatean como errores léxicos o sintácticos. |
| AST | `ast_handler`, creado por `crear_handler_ast()` | `mostrar_ast()` → `analizar_codigo()` | Obligatorio. | Ejecuta `Lexer` y `Parser` mediante `analizar_codigo()` y muestra la representación serializada del AST. |
| Sugerencias del Libro | `sugerencias_handler`, creado por `crear_handler_sugerencias()`; botón creado por `crear_boton_sugerencias_libro()` | `generar_reporte_sugerencias()` → `analizar_codigo()` → `generar_sugerencias()` | Obligatorio y previo al motor de sugerencias. | Valida primero con `Lexer` y `Parser`. Si hay errores, informa que deben corregirse antes de solicitar sugerencias. Si no hay errores, comprueba el motor opcional de sugerencias y agrupa las sugerencias por categorías pedagógicas. |
| Árbol de directorios | `reconstruir_arbol()`, `establecer_raiz_arbol_handler()` y `cargar_archivo_desde_evento_arbol()` | `normalizar_ruta_archivo_gui()`, `crear_arbol_directorios()`, `listar_directorio_cobra()` y `cargar_archivo_desde_arbol()` | No aplica. | Reconstruye el primer nivel visible cuando cambia la raíz, se abre un archivo o se guarda; las subcarpetas se cargan bajo demanda al expandirse con `crear_arbol_directorios()`. El campo `Raíz del árbol` pasa por `normalizar_ruta_archivo_gui()` y respeta el sandbox compartido. Solo los archivos `.co` y `.cobra` son cargables por defecto; el resto de entradas se rechaza antes de leerlas. |

## Restricción del selector de transpilación

El IDLE obtiene los lenguajes visibles con `gui_target_choices()` y los pasa a `crear_selector_target()` y `crear_switch_transpilacion()`. La especificación exige que esa lista permanezca limitada a:

1. `python`
2. `javascript`
3. `rust`

Cualquier cambio que muestre más opciones en la GUI debe considerarse una ruptura del contrato público documentado aquí y en la política de targets del proyecto.

## Flujo obligatorio para sugerencias

El flujo de **Sugerencias del Libro** es deliberadamente conservador:

1. Normalizar el contenido del editor.
2. Ejecutar `analizar_codigo()`.
3. Dentro de `analizar_codigo()`, ejecutar `Lexer(codigo).tokenizar()`.
4. Con esos tokens, ejecutar `Parser(tokens).parsear()`.
5. Solo si los pasos anteriores terminan sin excepción, consultar disponibilidad del motor opcional de sugerencias.
6. Solo con validación léxica y sintáctica exitosa, llamar a `generar_sugerencias(codigo)`.

Este orden evita generar recomendaciones sobre código que el compilador Cobra no puede tokenizar o parsear correctamente.
