# GUI / IDLE

El IDLE gráfico de pCobra vive en `src/pcobra/gui/idle.py` y reutiliza los helpers canónicos de `src/pcobra/gui/runtime.py` para mantener una sola implementación de la lógica de archivos, árbol, ejecución, transpilación, tokens, AST e inspección.

## Arranque

La forma recomendada para abrirlo desde la CLI es:

```bash
cobra gui
```

Para integraciones Flet o lanzamientos desde Python, usa el entrypoint canónico:

```python
from pcobra.gui.idle import main
```

También se mantiene el alias de compatibilidad:

```python
from pcobra.gui.app import main
```

El alias `pcobra.gui.app.main` delega en el IDLE canónico y no debe introducir una segunda lógica de archivo ni handlers alternativos para las mismas acciones.

## Flujo de análisis y acciones

El flujo funcional de la interfaz es:

1. **Editor Cobra:** el usuario escribe o carga código Cobra en el editor principal.
2. **Lexer:** antes de mostrar tokens, AST, sugerencias o ejecutar acciones que necesitan análisis, el contenido se tokeniza con el lexer del proyecto.
3. **Parser:** los tokens pasan por el parser para construir la representación sintáctica que consumen las acciones posteriores.
4. **Ejecución, transpilación o sugerencias:** con el código validado por el lexer y el parser, la GUI puede interpretar el programa, transpilarlo a un backend público o pedir sugerencias al motor IA oficial cuando esté disponible.

La barra de ejecución permite:

- **Ejecutar:** interpreta el código del editor con el runtime Cobra compartido.
- **Transpilar:** al activar el switch `Transpilar`, genera código únicamente para los backends públicos disponibles: `python`, `javascript` y `rust`.
- **Tokens:** muestra la tokenización del código actual.
- **AST:** muestra la representación del árbol sintáctico.
- **Sugerencias del Libro:** valida primero errores léxicos/sintácticos con `runtime.analizar_codigo`, que ejecuta `Lexer` y `Parser` como punto único de tokenización/parseo para la GUI. Solo si ambos pasos terminan sin errores, `runtime.generar_reporte_sugerencias` consulta el motor IA oficial, si está disponible, y muestra sugerencias.

Estos flujos se crean desde helpers de `runtime.py`: `crear_handler_ejecucion`, `crear_handler_tokens`, `crear_handler_ast` y `crear_handler_sugerencias`. Las acciones nuevas que quieran proponer correcciones tipográficas o sugerencias automáticas deben reutilizar `generar_reporte_sugerencias` —o una fachada equivalente que conserve el mismo prechequeo con `Lexer` y `Parser`— en lugar de llamar directamente al motor IA.

## Edición y estado de archivo

El editor permite modificar código Cobra de forma interactiva. La cabecera muestra el archivo activo o `Archivo nuevo (sin guardar)`, y añade un asterisco cuando el contenido del editor difiere del contenido cargado desde disco. La comparación de cambios se centraliza en `runtime.marcar_cambios_editor` para reflejar el estado de cambios sin guardar de manera consistente.

El control escogido para la edición es `CodeEditor` de `flet-code-editor`
0.86.1, sobre Flet 0.86.1. `runtime.crear_editor_codigo()` lo construye y lo
encapsula en `runtime.EditorCodigo`; `idle.py` consume únicamente las operaciones
del adaptador (contenido, limpieza y registro de callbacks), mientras el mismo
contrato también expone la solicitud de foco sin filtrar detalles del control.
Así, `idle.py` no depende de atributos propios de `CodeEditor`. Esta
separación mantiene en `idle.py` la coordinación de la interfaz y permite probar
el contrato del editor con dobles sin cargar el control gráfico real.

La indentación del editor usa **cuatro espacios por nivel**:

- Tab sin selección inserta cuatro espacios en la posición del cursor.
- Tab con una selección multilínea añade cuatro espacios al comienzo de cada
  línea intersectada; una selección que termina justo al inicio de la línea
  siguiente no incluye esa línea.
- Shift+Tab desindenta cada línea intersectada, retirando hasta cuatro espacios
  iniciales o un tabulador literal, sin borrar texto que no sea indentación.
- La selección y el cursor se desplazan junto con el texto, incluidas selecciones
  invertidas y finales de línea LF o CRLF.

Tab y Shift+Tab los procesa localmente `CodeEditor`; el IDLE no registra un
atajo global en `Page`, porque eso duplicaría la edición. La función pura
`runtime.ajustar_indentacion_editor()` expresa y prueba el contrato de cuatro
espacios, pero no se conecta como segundo manejador de teclado.

## Acciones de archivo y guardado

La barra de archivo expone estas acciones:

- **Nuevo:** reinicia el estado del editor con un archivo en memoria sin ruta activa mediante `runtime.crear_archivo_nuevo_en_editor`.
- **Abrir:** carga la ruta indicada en el campo `Ruta` mediante `runtime.abrir_archivo_desde_ruta`.
- **Guardar:** escribe el contenido del editor sobre el archivo activo con `runtime.guardar_archivo_activo`; si todavía no existe ruta activa, redirige al flujo de **Guardar como**.
- **Guardar como:** escribe el contenido del editor en la ruta indicada mediante `runtime.guardar_archivo_como` y actualiza esa ruta como archivo activo.
- **Recargar:** vuelve a leer desde disco el archivo activo mediante `runtime.recargar_archivo_activo`.

Todas las lecturas y escrituras de archivos de texto Cobra se tratan como UTF-8. Si hay cambios sin guardar, la interfaz conserva el indicador visual hasta que el contenido del editor coincide de nuevo con el contenido persistido. Toda lectura, escritura y normalización de rutas se mantiene en `src/pcobra/gui/runtime.py`; `src/pcobra/gui/idle.py` solo coordina eventos Flet, estado visual y mensajes.

## Árbol de directorios y archivos auxiliares

El panel lateral muestra un árbol de directorios construido con `runtime.crear_arbol_directorios`. La raíz inicial es el directorio de trabajo actual y puede cambiarse desde el campo `Raíz del árbol` con el botón **Establecer raíz**; por tanto, la raíz es editable desde la propia GUI.

El árbol muestra directorios y archivos de texto del proyecto activo clasificados por `runtime.detectar_tipo_archivo()`. Los tipos visibles y soportados incluyen archivos Cobra (`.co` y `.cobra`), Markdown (`.md` y `.markdown`), TXT, configuración JSON/YAML/TOML, `Dockerfile` y variantes `Dockerfile.*`, `.gitignore`, `.dockerignore` y `.env.example`. Los subdirectorios se cargan bajo demanda al expandirlos; los archivos que no encajan en esos tipos permanecen fuera del árbol salvo que una configuración interna futura active la exposición de desconocidos como texto plano.

Al seleccionar un archivo visible, el IDLE llama a `runtime.cargar_archivo_desde_arbol`, comprueba que sea un archivo de texto soportado y reutiliza el mismo flujo de apertura para cargarlo en el editor. Los archivos auxiliares se pueden abrir, editar, guardar, recargar y borrar como texto dentro del proyecto activo, pero no participan en el análisis Cobra. Solo los archivos Cobra habilitan **Ejecutar**, **Tokens**, **AST**, **Sugerencias del Libro** y **Corrección**; por tanto, el `Lexer` y el `Parser` se usan explícitamente solo con archivos Cobra.

## Disponibilidad de dependencias y degradación

- **Flet y editor:** `flet==0.86.1` y `flet-code-editor==0.86.1` están declarados
  como dependencias del proyecto. Sus imports siguen siendo diferidos: importar
  módulos CLI no debe cargar Flet ni el editor; abrir el IDLE sí los requiere. Si
  alguno no está disponible en una instalación parcial, el intento de iniciar la
  GUI debe identificar la dependencia faltante sin romper los flujos no
  gráficos.
- **Motor IA de sugerencias:** `agix` es una dependencia oficial declarada en `[project].dependencies`, no un extra opcional. Su ausencia solo se tolera para instalaciones parciales o entornos headless: en ese caso, el botón de sugerencias aparece deshabilitado o muestra el motivo y la forma de instalarla. La ejecución, los tokens, el AST, la transpilación y las acciones de archivo siguen disponibles porque no deben importar el motor hasta que se soliciten sugerencias.

## Plataformas y validación manual

No hay una ejecución manual completa registrada para ninguna plataforma. Por
tanto, este documento **no afirma compatibilidad** con Linux, Windows ni macOS a
partir de las pruebas unitarias o de la inspección del control. La matriz
reproducible y el criterio para registrar una plataforma verificada están en
[`docs/gui_idle_especificacion.md`](gui_idle_especificacion.md); la evidencia y
el estado actual se reflejan en
[`docs/gui_idle_trazabilidad.md`](gui_idle_trazabilidad.md).

## Empaquetar proyectos desde el IDLE

El botón **Empaquetar** construye un artefacto instalable del proyecto activo usando la misma capa que `cobra installer build .`. El usuario debe abrir o crear un proyecto, pulsar **Empaquetar**, seleccionar `onedir` o `onefile` y confirmar. `onedir` genera una carpeta distribuible; `onefile` genera un ejecutable único con extracción temporal al arrancar.

Si no hay proyecto o ruta activa, el IDLE muestra un aviso antes de invocar el build. Para detalles de CLI, cross-compilation, Docker/VM/CI, manifiesto `cobra_build_manifest.json` y solución de errores, consulta [`docs/cobra_installer.md`](cobra_installer.md).
