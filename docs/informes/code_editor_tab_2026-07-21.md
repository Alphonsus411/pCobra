# Verificación de Tab en `CodeEditor` (2026-07-21)

`flet-code-editor` 0.86.1 no publica un evento de teclado local. Su API pública
documentada ofrece `value`, `selection`, `on_change`, `on_selection_change` y
`focus()`, que son las únicas operaciones usadas por el adaptador de pCobra.

No se añadió captura global en `Page`: el control ya procesa internamente Tab y
Shift+Tab. La implementación Flutter que distribuye Flet registra `IndentIntent`
para Tab y `OutdentIntent` para Shift+Tab en los atajos locales de `CodeField`.
Duplicarlos desde Python produciría dos modificaciones por pulsación.

## Reproducción

1. Instalar las versiones auditadas:
   `python -m pip install flet==0.86.1 flet-code-editor==0.86.1`.
2. Comprobar la superficie pública con:
   `python -c "import flet_code_editor as f; print(f.CodeEditor.__annotations__)"`.
3. Ejecutar una app mínima con `CodeEditor(value="uno\ndos")`, seleccionar ambas
   líneas y pulsar Tab y Shift+Tab. Tab indenta la selección y Shift+Tab la
   desindenta sin que la aplicación registre un manejador de teclado.
4. La asociación reproducible de atajos se encuentra en
   `lib/src/code_field/code_field.dart` del paquete base
   [`flutter_code_editor`](https://github.com/akvelon/flutter-code-editor/blob/main/lib/src/code_field/code_field.dart).

La función pura `ajustar_indentacion_editor` conserva un contrato verificable
para texto y offsets, pero deliberadamente no se conecta a una captura de
teclado: `CodeEditor` resuelve esas teclas localmente.
