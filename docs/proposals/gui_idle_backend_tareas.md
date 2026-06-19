# Tareas estructuradas — GUI IDLE, sugerencias y backends oficiales

Fecha: 2026-06-19

## Decisiones verificadas

- El backend público del proyecto queda limitado a los tres pilares canónicos: `python`, `javascript` y `rust`.
- No se reintroducen targets legacy como `go`, `cpp`, `java`, `wasm` o `asm` en la GUI ni en la política pública de backend.
- La GUI debe consumir la lista canónica desde `PUBLIC_BACKENDS`/`OFFICIAL_TARGETS`, nunca una lista local duplicada.
- No se cambia el contrato Lexer/Parser para estas tareas. Toda sugerencia automática debe validar primero el código de entrada y después validar los fragmentos sugeridos con `Lexer(codigo).tokenizar()` y `Parser(tokens).parsear()`.
- La librería presente y documentada para sugerencias es `agix`. La mención `agi-core` se considera incoherencia nominal si aparece en requisitos externos: no existe como dependencia declarada del proyecto, por lo que no debe inventarse una integración paralela sin ADR aprobada.

## Estado general de la propuesta GUI

La revisión de `src/pcobra/gui/idle.py`, `src/pcobra/gui/runtime.py` y sus pruebas asociadas confirma que las funcionalidades base del IDLE gráfico ya están implementadas. Esta propuesta queda actualizada para separar explícitamente:

- **Implementado:** piezas ya presentes y cubiertas por pruebas.
- **Pendiente:** mejoras futuras que no requieren cambiar gramática ni añadir sintaxis Cobra.
- **Verificaciones automáticas:** pruebas que deben seguir pasando para preservar el contrato.

## Tarea GUI-01 — Guardado de archivos en el IDLE

**Estado:** Implementado.

**Objetivo:** mantener una experiencia tipo IDLE para crear, abrir, guardar, guardar como y recargar archivos Cobra.

**Alcance implementado:**

- Crear un archivo nuevo en memoria desde el IDLE.
- Abrir archivos desde una ruta escrita por el usuario.
- Guardar el archivo activo si ya existe una ruta asociada.
- Guardar como en una ruta indicada por el usuario y actualizar el estado activo.
- Recargar el archivo activo desde disco.
- Usar `GuiFileState` para ruta activa, contenido cargado y marca de cambios sin guardar.
- Guardar solo texto normalizado del editor.
- Aceptar extensiones Cobra documentadas: `.co` y `.cobra`.
- Mostrar errores de ruta, permisos, Unicode y validación en el panel de salida.

**Evidencia:**

- Código: `src/pcobra/gui/runtime.py` define `GuiFileState`, `nuevo_archivo`, `abrir_archivo_desde_ruta`, `guardar_archivo_activo`, `guardar_archivo_como`, `recargar_archivo_activo`, `crear_titulo_archivo` y helpers de lectura/escritura.
- Código: `src/pcobra/gui/idle.py` conecta los botones `Nuevo`, `Abrir`, `Guardar`, `Guardar como` y `Recargar` con los helpers del runtime, además de mantener la etiqueta visual del archivo activo.
- Pruebas: `tests/unit/test_gui_idle.py::test_main_acciones_publicas_de_archivo` cubre las acciones públicas de archivo en la GUI sin depender de Flet real.
- Pruebas: `tests/gui/test_runtime_file_helpers.py` y `tests/unit/test_gui_runtime.py` cubren extensiones Cobra, lectura/escritura, normalización y errores de helpers.

**Pendiente real:**

- Evaluar en una historia separada si se expone un selector nativo de archivos además del campo de ruta. Esta mejora no cambia la gramática Cobra ni introduce sintaxis nueva.

**Verificaciones automáticas:**

- `pytest tests/unit/test_gui_idle.py::test_main_acciones_publicas_de_archivo`
- `pytest tests/gui/test_runtime_file_helpers.py`
- `pytest tests/unit/test_gui_runtime.py`

## Tarea GUI-02 — Árbol de directorios Cobra

**Estado:** Implementado.

**Objetivo:** mostrar un explorador lateral seguro para proyectos Cobra.

**Alcance implementado:**

- Renderizar directorios y archivos `.co`/`.cobra` por defecto.
- Permitir cambiar la raíz del árbol desde la GUI.
- Cargar archivos Cobra al seleccionarlos desde el árbol.
- Mantener una opción interna para mostrar todos los archivos solo como configuración futura.
- Ordenar directorios antes que archivos de forma estable.
- Rechazar archivos no Cobra al cargarlos desde el árbol sin alterar el contenido activo.

**Evidencia:**

- Código: `src/pcobra/gui/runtime.py` define `COBRA_FILE_EXTENSIONS`, `MOSTRAR_TODOS_LOS_ARCHIVOS_IDLE`, `es_archivo_cobra`, `listar_directorio_cobra`, `construir_entradas_directorio`, `crear_arbol_directorios` y `cargar_archivo_desde_arbol`.
- Código: `src/pcobra/gui/idle.py` crea el panel de árbol, reconstruye el árbol al cambiar de raíz, carga archivos desde eventos del árbol y valida que la raíz sea un directorio.
- Pruebas: `tests/unit/test_gui_idle.py::test_main_acciones_publicas_de_archivo` verifica la carga desde el árbol.
- Pruebas: `tests/unit/test_gui_idle.py::test_main_establecer_raiz_arbol_valida_directorios` verifica el cambio de raíz y la validación de directorios.
- Pruebas: `tests/gui/test_runtime_file_helpers.py` y `tests/unit/test_gui_runtime.py` verifican filtrado por extensiones, orden estable y opción interna `mostrar_todos`.

**Pendiente real:**

- Documentar y diseñar, si se aprueba, una preferencia de usuario para activar `mostrar_todos`. Mientras tanto debe seguir siendo una opción interna y no una promesa de UX pública.

**Verificaciones automáticas:**

- `pytest tests/unit/test_gui_idle.py::test_main_establecer_raiz_arbol_valida_directorios`
- `pytest tests/gui/test_runtime_file_helpers.py`
- `pytest tests/unit/test_gui_runtime.py`

## Tarea GUI-03 — Tokens y AST en el IDLE

**Estado:** Implementado.

**Objetivo:** inspeccionar el resultado del Lexer y del Parser desde la GUI sin alterar el contrato de gramática.

**Alcance implementado:**

- Botón `Tokens` conectado a un handler común del runtime.
- Botón `AST` conectado a un handler común del runtime.
- Uso de `Lexer(codigo).tokenizar()` y `Parser(tokens).parsear()` mediante `analizar_codigo`.
- Presentación de errores léxicos/sintácticos formateados en el panel de salida.

**Evidencia:**

- Código: `src/pcobra/gui/runtime.py` define `analizar_codigo`, `mostrar_tokens`, `mostrar_ast`, `crear_handler_tokens` y `crear_handler_ast`.
- Código: `src/pcobra/gui/idle.py` crea los botones `Tokens` y `AST` y los conecta a esos handlers.
- Pruebas: `tests/unit/test_gui_runtime.py::test_ejecutar_transpilar_tokens_y_ast` cubre tokenización y AST desde el runtime.
- Pruebas: `tests/unit/test_gui_idle.py` cubre que los botones `Tokens` y `AST` se renderizan y ejecutan sus handlers.
- Pruebas: `tests/gui/test_runtime_file_helpers.py` verifica el flujo Lexer/Parser/ejecución con dobles controlados.

**Pendiente real:**

- Ninguna mejora funcional obligatoria detectada para esta propuesta. Cualquier mejora visual futura debe limitarse a presentación y no modificar gramática.

**Verificaciones automáticas:**

- `pytest tests/unit/test_gui_runtime.py::test_ejecutar_transpilar_tokens_y_ast`
- `pytest tests/unit/test_gui_idle.py`
- `pytest tests/gui/test_runtime_file_helpers.py`

## Tarea GUI-04 — Sugerencias del Libro

**Estado:** Implementado en la GUI y el runtime; pendiente solo la disponibilidad opcional del motor externo cuando no esté instalado.

**Objetivo:** ofrecer sugerencias de código trazables al Libro de Programación sin inventar sintaxis.

**Alcance implementado:**

- Usar la fachada `pcobra.ia.analizador_sugerencias` bajo demanda.
- Mantener `agix` como nombre canónico del motor opcional.
- Rechazar `agi-core` como nombre de dependencia mientras no exista una ADR aprobada.
- Agrupar sugerencias por categorías: léxico/sintaxis, estilo, nombres, forma canónica y observabilidad.
- Validar la entrada con Lexer/Parser antes de solicitar sugerencias.
- Bloquear correcciones aplicables cuando el código no parsea.
- Deshabilitar o explicar el botón cuando falta `agix`.

**Evidencia:**

- Código: `src/pcobra/gui/runtime.py` define `CANONICAL_SUGGESTION_ENGINE = "agix"`, `detectar_motor_ia_sugerencias`, `generar_sugerencias`, `generar_reporte_sugerencias`, clasificación por categorías y `crear_handler_sugerencias`.
- Código: `src/pcobra/gui/runtime.py` conserva `crear_handler_sugerencias_agix` solo como alias interno de compatibilidad deprecado.
- Código: `src/pcobra/gui/idle.py` crea el botón `Sugerencias del Libro` con `crear_boton_sugerencias_libro` y el handler común de sugerencias.
- Pruebas: `tests/unit/test_gui_idle.py` cubre botón habilitado/deshabilitado, tooltip cuando falta `agix` y ejecución del handler.
- Pruebas: `tests/unit/test_gui_runtime.py` cubre validación previa con Lexer/Parser, errores de Lexer/Parser sin correcciones, ausencia del motor opcional y alias deprecado.
- Pruebas: `tests/gui/test_auto_suggestion_parser_contract.py` verifica que los fragmentos sugeridos parsean y que las formas inválidas permanecen inválidas.

**Pendiente real:**

- Mantener una ADR separada si algún requisito externo propone cambiar de `agix` a otro motor o integrar un motor adicional.
- Ampliar reglas internas de sugerencia solo cuando cada fragmento sugerido sea validado por Lexer/Parser y tenga trazabilidad al Libro. No se debe introducir sintaxis nueva desde esta documentación.

**Verificaciones automáticas:**

- `pytest tests/unit/test_gui_idle.py`
- `pytest tests/unit/test_gui_runtime.py`
- `pytest tests/gui/test_auto_suggestion_parser_contract.py`

## Tarea BACKEND-01 — Tres pilares oficiales

**Estado:** Implementado como política normativa; requiere verificación continua.

**Objetivo:** asegurar que el backend público esté conformado solo por Python, JavaScript y Rust.

**Alcance vigente:**

- Mantener `PUBLIC_BACKENDS = ("python", "javascript", "rust")` como fuente normativa.
- Mantener `ALLOWED_TARGETS`, `OFFICIAL_TARGETS`, GUI y CLI alineados con esa tupla.
- No incluir alias cortos retirados en superficies públicas, aunque puedan existir shims internos documentados.

**Evidencia:**

- Código: la GUI obtiene las opciones públicas mediante helpers del runtime en lugar de una lista local duplicada.
- Pruebas: la suite de runtime GUI incluye contratos para opciones públicas y ausencia de backends legacy en la superficie de GUI.

**Pendiente real:**

- Mantener una auditoría periódica para que las rutas legacy no reaparezcan en documentación pública ni en opciones visibles de GUI/CLI.

**Verificaciones automáticas:**

- `pytest tests/unit/test_gui_runtime.py`

## Tarea QA-01 — Coherencia Lexer/Parser

**Estado:** Implementado como contrato de verificación automática.

**Objetivo:** evitar divergencias entre documentación, sugerencias y gramática implementada.

**Alcance vigente:**

- No modificar tokens ni parser para introducir atajos no documentados.
- Añadir nuevas reglas de sugerencia solo si sus fragmentos válidos parsean.
- Documentar cualquier incoherencia como tarea de mejora antes de cambiar sintaxis.

**Evidencia:**

- Código: `src/pcobra/gui/runtime.py` centraliza el análisis en `analizar_codigo` y lo usa antes de ejecutar, transpilar, mostrar tokens, mostrar AST y generar sugerencias.
- Pruebas: `tests/gui/test_auto_suggestion_parser_contract.py` valida fragmentos sugeridos y fragmentos inválidos contra el Parser real.
- Pruebas: `tests/unit/test_gui_runtime.py` comprueba que el reporte de sugerencias valida antes de llamar al motor opcional.

**Pendiente real:**

- Añadir tests de contrato cuando se incorporen nuevas reglas de sugerencia. La documentación no debe ser usada para cambiar la gramática directamente.

**Verificaciones automáticas:**

- `pytest tests/gui/test_auto_suggestion_parser_contract.py`
- `pytest tests/unit/test_gui_runtime.py`

## Incoherencias detectadas y tareas de mejora

1. **Nombre `agi-core` vs `agix`:** el proyecto declara y documenta `agix`; no se encontró una dependencia canónica `agi-core`.  
   **Mejora propuesta:** normalizar nuevas historias de usuario y documentación a `agix`, o abrir y aprobar una ADR separada si se decide migrar realmente a otra librería o añadir una integración paralela.
2. **Shims legacy internos:** existen menciones históricas y rutas de compatibilidad.  
   **Mejora propuesta:** mantenerlas fuera de la UX pública y revisar su eliminación según el calendario de compatibilidad.
3. **Validadores legacy:** cualquier validador fuera de Python/JavaScript/Rust debe permanecer en rutas internas de regresión histórica.  
   **Mejora propuesta:** auditar periódicamente documentación pública con un lint que bloquee promoción de targets legacy.
