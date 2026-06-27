# Especificación del IDLE gráfico Cobra

Esta especificación define el alcance funcional del IDLE gráfico Cobra (`pcobra.gui.idle`) y el contrato de comportamiento esperado para su runtime (`pcobra.gui.runtime`). Debe mantenerse alineada con la matriz de trazabilidad en [`docs/gui_idle_trazabilidad.md`](gui_idle_trazabilidad.md) y con el contrato pedagógico del Libro §3.9.

## Estado

- IDLE básico funcional para 10.1.1.
- Alcance: edición, proyectos, archivos, ejecución, tokens, AST, sugerencias, corrección y borrado seguro.
- No es un IDE completo: prioriza flujos simples, verificables y seguros para trabajo local con archivos Cobra.
- El selector de transpilación del IDLE solo puede mostrar los targets públicos canónicos: `python`, `javascript` y `rust`. No debe exponer aliases, targets legacy ni backends experimentales.

## Workspace

- El workspace por defecto es `~/CobraProjects`.
- El IDLE crea el workspace si no existe.
- No se deben guardar proyectos de usuario dentro del repositorio pCobra ni bajo `src/`.
- El workspace actúa como contenedor de proyectos de usuario y como límite superior para operaciones de gestión de proyectos.

## Proyecto activo

- Un proyecto activo debe ser hijo directo del workspace.
- Si `project_root == workspace_root`, no hay proyecto activo.
- Las operaciones de archivo requieren proyecto activo.
- Abrir o crear un proyecto establece `project_root` como raíz operativa para las acciones sobre archivos.
- Cerrar el proyecto activo devuelve el estado del IDLE a workspace sin proyecto activo y bloquea operaciones que dependan de archivos de proyecto.

## Operaciones soportadas

| Operación | Comportamiento esperado | Requisito Lexer/Parser |
| --- | --- | --- |
| Crear proyecto | Crea un directorio hijo directo del workspace, lo establece como proyecto activo y reconstruye el árbol lateral. | No aplica. |
| Abrir proyecto | Abre un directorio existente que sea hijo directo del workspace y lo establece como proyecto activo. | No aplica. |
| Cerrar proyecto | Limpia el proyecto activo, conserva el workspace y bloquea operaciones de archivo hasta abrir o crear otro proyecto. | No aplica. |
| Nuevo archivo en memoria | Limpia el editor, reinicia el estado del archivo activo y marca el contenido como archivo nuevo sin ruta. | No aplica. |
| Abrir archivo | Lee un archivo ubicado dentro del proyecto activo y actualiza el editor y el estado del archivo activo. | No aplica. |
| Guardar | Guarda el contenido del editor en la ruta activa si existe; si no existe, deriva a Guardar como. | No aplica. |
| Guardar como | Guarda el contenido del editor en una ruta resuelta dentro del proyecto activo y actualiza la ruta activa. | No aplica. |
| Recargar | Vuelve a leer desde disco el archivo activo y reemplaza el contenido del editor. | No aplica. |
| Ejecutar | Normaliza el texto del editor, analiza el código y entrega el AST al intérprete Cobra. | Obligatorio. |
| Tokens | Analiza el código y muestra una línea por token o el diagnóstico de error correspondiente. | Obligatorio. |
| AST | Analiza el código y muestra una representación serializada del AST o el diagnóstico de error correspondiente. | Obligatorio. |
| Sugerencias del Libro | Valida el código y, solo si no hay errores léxicos ni sintácticos, genera sugerencias pedagógicas agrupadas por categoría. | Obligatorio y previo. |
| Corrección | Valida el código y, solo si no hay errores léxicos ni sintácticos, genera un reporte tipográfico/estilístico no destructivo. | Obligatorio y previo. |
| Eliminar archivo | Elimina un archivo dentro del proyecto activo, aplicando confirmación mínima y actualización posterior del estado del editor. | No aplica. |
| Eliminar carpeta | Elimina una carpeta dentro del proyecto activo sin permitir que `project_root` se borre como carpeta normal. | No aplica. |
| Eliminar proyecto | Elimina el proyecto activo solo si es hijo directo del workspace y deja el IDLE sin proyecto activo. | No aplica. |

## Tipos de archivo soportados

El IDLE puede abrir, editar, guardar, recargar y borrar archivos de texto del proyecto con los siguientes nombres o extensiones:

- Archivos Cobra: `.cobra`, `.co`.
- Markdown: `.md`, `.markdown`.
- Texto plano: `.txt`.
- Configuración y datos: `.json`, `.yml`, `.yaml`, `.toml`.
- Docker: `Dockerfile`, `Dockerfile.*`.
- Ignorados de herramientas: `.gitignore`, `.dockerignore`.
- Plantillas de entorno: `.env.example`.

Estos archivos auxiliares forman parte del proyecto activo y se gestionan con las mismas operaciones seguras de archivos, pero no amplían la gramática Cobra ni el alcance del compilador/intérprete.

## Acciones Cobra solo para archivos Cobra

Las acciones **Ejecutar**, **Tokens**, **AST**, **Sugerencias del Libro** y **Corrección** solo están disponibles cuando el archivo activo es Cobra (`.cobra` o `.co`). Los archivos auxiliares nunca se envían a `Lexer` ni a `Parser`; por tanto, solo pueden participar en operaciones de edición y gestión de archivos.

La seguridad de rutas existente se conserva para todos los tipos soportados: se requiere proyecto activo, se bloquean escapes con `../` o equivalentes, se bloquean rutas absolutas externas y se impide usar como proyectos directorios ubicados bajo el repositorio pCobra o bajo `src/`.

## Seguridad de rutas

- Toda ruta relativa de archivo o carpeta se resuelve contra `project_root`.
- Se bloquea cualquier ruta con escape mediante `../` o equivalentes que salga del proyecto activo.
- Se bloquean rutas absolutas fuera del proyecto activo.
- Se bloquean operaciones de archivo sin proyecto activo.
- Se bloquea la eliminación de `project_root` como carpeta normal; para borrar un proyecto debe usarse la operación específica de eliminación de proyecto.
- Se bloquea la eliminación de `workspace_root`.
- La eliminación de proyecto solo está permitida si el proyecto activo es hijo directo del workspace.
- La gestión del árbol de archivos es funcionalidad de archivos/rutas de la GUI: no afecta la sintaxis Cobra y no debe requerir cambios en `Lexer` ni `Parser`.

## Sugerencias y Corrección

- Las acciones **Sugerencias del Libro** y **Corrección** deben validar previamente el contenido con `Lexer(codigo).tokenizar()` y `Parser(tokens).parsear()`.
- No se deben invocar sugerencias ni corrección aplicable si existe un error léxico o sintáctico.
- Si la validación falla, el IDLE debe mostrar el diagnóstico correspondiente y no debe invocar el motor IA opcional.
- Ninguna acción debe modificar automáticamente el contenido del editor.
- **Sugerencias del Libro** muestra recomendaciones pedagógicas agrupadas por categoría.
- **Corrección** genera un reporte tipográfico/estilístico no destructivo para revisión humana.
- El flujo debe respetar el contrato del Libro §3.9.
- El motor IA canónico para sugerencias es `agix`; `agi-core` no debe usarse como sustituto ni dependencia paralela sin una ADR nueva. La decisión vigente está documentada en [`docs/ADR/002-motor-ia-sugerencias-agix.md`](ADR/002-motor-ia-sugerencias-agix.md).

## Borrado seguro

- Eliminar archivo opera sobre el archivo activo.
- Eliminar carpeta opera sobre la ruta indicada o seleccionada dentro del proyecto activo.
- Eliminar proyecto opera solo sobre el proyecto activo.
- Deben existir confirmaciones mínimas antes del borrado de archivos, carpetas o proyectos.
- Tras borrar el archivo activo, el editor queda en estado de archivo nuevo en memoria, sin ruta activa asociada, y el árbol lateral se reconstruye.
- Tras borrar el proyecto activo, el IDLE queda sin proyecto activo, con las operaciones de archivo bloqueadas hasta crear o abrir otro proyecto, y el árbol lateral vuelve al estado de workspace.
- La eliminación de carpeta no puede usarse para borrar `project_root` ni `workspace_root`.

## POCs validados manualmente

| POC | Validación manual | Estado |
| --- | --- | --- |
| POC-1 | Arranque del IDLE y creación automática del workspace por defecto. | 🟢 Verde |
| POC-2 | Crear proyecto como hijo directo del workspace. | 🟢 Verde |
| POC-3 | Abrir proyecto existente como hijo directo del workspace. | 🟢 Verde |
| POC-4 | Cerrar proyecto activo y bloquear operaciones que requieren proyecto. | 🟢 Verde |
| POC-5 | Nuevo archivo en memoria dentro del flujo del editor. | 🟢 Verde |
| POC-6 | Abrir archivo del proyecto activo. | 🟢 Verde |
| POC-7 | Guardar y Guardar como dentro del proyecto activo. | 🟢 Verde |
| POC-8 | Recargar archivo activo desde disco. | 🟢 Verde |
| POC-9 | Ejecutar código Cobra validado con Lexer y Parser. | 🟢 Verde |
| POC-10 | Mostrar tokens y AST desde código validado. | 🟢 Verde |
| POC-11A | Sugerencias del Libro con código válido. | 🟢 Verde |
| POC-11B | Corrección con código válido. | 🟢 Verde |
| POC-11C | Bloqueo de sugerencias ante error léxico. | 🟢 Verde |
| POC-11D | Bloqueo de corrección ante error sintáctico. | 🟢 Verde |
| POC-11E | Bloqueo de rutas con `../` fuera del proyecto activo. | 🟢 Verde |
| POC-11F | Bloqueo de rutas absolutas fuera del proyecto activo. | 🟢 Verde |
| POC-11G | Eliminación segura de archivo activo. | 🟢 Verde |
| POC-11H | Eliminación segura de carpeta interna del proyecto. | 🟢 Verde |
| POC-11I | Eliminación segura de proyecto activo hijo directo del workspace. | 🟢 Verde |

## POCs pendientes/esperadas

| POC | Validación esperada | Estado |
| --- | --- | --- |
| POC-13A | Abrir, editar, guardar y recargar archivos Cobra (`.cobra`, `.co`) dentro del proyecto activo. | 🟢 Verde |
| POC-13B | Abrir, editar, guardar y recargar archivos auxiliares de documentación/texto (`.md`, `.markdown`, `.txt`) sin invocar `Lexer` ni `Parser`. | 🟢 Verde |
| POC-13C | Abrir, editar, guardar y recargar archivos auxiliares de configuración/datos (`.json`, `.yml`, `.yaml`, `.toml`) sin invocar `Lexer` ni `Parser`. | 🟢 Verde |
| POC-13D | Abrir, editar, guardar y recargar archivos Docker (`Dockerfile`, `Dockerfile.*`) y de ignorados (`.gitignore`, `.dockerignore`) sin invocar `Lexer` ni `Parser`. | 🟢 Verde |
| POC-13E | Abrir, editar, guardar y recargar `.env.example` sin invocar `Lexer` ni `Parser`. | 🟢 Verde |
| POC-13F | Bloquear **Ejecutar**, **Tokens**, **AST**, **Sugerencias del Libro** y **Corrección** para todo archivo que no sea `.cobra` ni `.co`, conservando las restricciones de rutas existentes. | 🟢 Verde |

## Limitaciones conocidas

- El menú contextual del árbol lateral queda para fase posterior.
- La confirmación avanzada de borrado puede evolucionar.
- No es IDE completo, sino IDLE básico funcional.
