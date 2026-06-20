# Capacidades actuales del IDLE gráfico

El IDLE gráfico de pCobra vive en `src/pcobra/gui/idle.py` y reutiliza los helpers canónicos de `src/pcobra/gui/runtime.py` para mantener una sola implementación de la lógica de archivos, árbol, ejecución e inspección.

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

## Edición y estado de archivo

El editor permite modificar código Cobra de forma interactiva. La cabecera muestra el archivo activo o `Archivo nuevo (sin guardar)`, y añade un asterisco cuando el contenido del editor difiere del contenido cargado desde disco. La comparación de cambios se centraliza en `runtime.marcar_cambios_editor`.

## Acciones de archivo

La barra de archivo expone estas acciones:

- **Nuevo:** reinicia el estado del editor con un archivo en memoria sin ruta activa mediante `runtime.crear_archivo_nuevo_en_editor`.
- **Abrir:** carga la ruta indicada en el campo `Ruta` mediante `runtime.abrir_archivo_desde_ruta`.
- **Guardar:** escribe el archivo activo con `runtime.guardar_archivo_activo`; si todavía no existe ruta activa, redirige al flujo de **Guardar como**.
- **Guardar como:** escribe el contenido del editor en la ruta indicada mediante `runtime.guardar_archivo_como`.
- **Recargar:** vuelve a leer desde disco el archivo activo mediante `runtime.recargar_archivo_activo`.

Toda lectura, escritura y normalización de rutas se mantiene en `src/pcobra/gui/runtime.py`. `src/pcobra/gui/idle.py` solo coordina eventos Flet, estado visual y mensajes.

## Árbol de directorios

El panel lateral muestra un árbol de directorios construido con `runtime.crear_arbol_directorios`. La raíz inicial es el directorio de trabajo actual y puede cambiarse desde el campo `Raíz del árbol` con el botón **Establecer raíz**.

El árbol carga subdirectorios bajo demanda al expandirlos. Al seleccionar un archivo Cobra visible, el IDLE llama a `runtime.cargar_archivo_desde_arbol`, que valida la extensión y reutiliza el mismo flujo de apertura de archivos.

## Ejecución, transpilación, tokens, AST y sugerencias

La barra de ejecución permite:

- **Ejecutar:** interpreta el código del editor con el runtime Cobra compartido.
- **Transpilar:** al activar el switch `Transpilar`, genera código para el target seleccionado en el desplegable.
- **Tokens:** muestra la tokenización del código actual.
- **AST:** muestra la representación del árbol sintáctico.
- **Sugerencias del Libro:** valida primero errores léxicos/sintácticos con `runtime.analizar_codigo`, que ejecuta `Lexer` y `Parser` como punto único de tokenización/parseo para la GUI. Solo si ambos pasos terminan sin errores, `runtime.generar_reporte_sugerencias` consulta el motor IA opcional y muestra sugerencias.

Estos flujos se crean desde helpers de `runtime.py`: `crear_handler_ejecucion`, `crear_handler_tokens`, `crear_handler_ast` y `crear_handler_sugerencias`. Las acciones nuevas que quieran proponer correcciones tipográficas o sugerencias automáticas deben reutilizar `generar_reporte_sugerencias` —o una fachada equivalente que conserve el mismo prechequeo con `Lexer` y `Parser`— en lugar de llamar directamente al motor IA.

## Limitaciones actuales

- El árbol de directorios muestra directorios y archivos Cobra con extensión `.co` o `.cobra` por defecto; otros archivos quedan ocultos salvo que se active una configuración interna futura para mostrar todo.
- Flet es una dependencia opcional de la GUI. Importar módulos CLI no debe requerir Flet; abrir el IDLE sí requiere instalarlo.
- Las sugerencias dependen del motor IA declarado por el proyecto (`agix`). Si la dependencia opcional no está disponible, el botón aparece deshabilitado o informa el motivo.
