# Validación manual del IDLE — 2026-06-22

## Arranque local

Comando usado en este entorno Linux del repositorio:

```bash
python -m pcobra.gui.idle
```

También se intentó primero el ejemplo equivalente a entorno virtual local:

```bash
.venv/bin/python -m pcobra.gui.idle
```

Ese segundo comando no aplica aquí porque no existe `.venv/bin/python` en el contenedor.

## Resultado en el contenedor

El arranque con `python -m pcobra.gui.idle` inició Flet y descargó/instaló `flet-web 0.28.3`; el proceso se cortó con `timeout 10s` para no dejar una aplicación gráfica abierta en un entorno no interactivo. Por esa limitación del contenedor no se pudieron completar clics manuales reales sobre la ventana.

## Validación paso a paso solicitada

| Paso solicitado | Resultado en este entorno |
| --- | --- |
| Abrir `proyecto_beta`. | Cubierto por prueba automatizada de apertura/creación de proyecto; pendiente de clic manual real por entorno no interactivo. |
| Abrir `src\principal.cobra`. | Pendiente de clic manual real; la suite cubre resolución segura de rutas dentro del proyecto. |
| Ejecutar. | Pendiente de clic manual real. |
| Tokens. | Pendiente de clic manual real. |
| AST. | Pendiente de clic manual real. |
| Sugerencias del Libro. | Validado por contrato automatizado de parser/sugerencias. |
| Corrección. | Validado por pruebas automatizadas de corrección tipográfica. |
| Cerrar proyecto. | Validado por prueba automatizada: reinicia al workspace, limpia el editor y no borra/escribe archivos. |
| Intentar operación de archivo sin proyecto activo. | Validado por prueba automatizada: muestra `Crea o abre un proyecto antes de trabajar con archivos.` |
| Crear proyecto temporal. | Cubierto por pruebas automatizadas de creación de proyecto. |
| Eliminar archivo con doble confirmación. | Validado por pruebas automatizadas de doble pulsación. |
| Eliminar carpeta con doble confirmación. | Validado por pruebas automatizadas de doble pulsación. |
| Eliminar proyecto con confirmación. | Validado por pruebas automatizadas de confirmación. |

## POC específicas

| POC | Resultado |
| --- | --- |
| POC-12A: abrir `proyecto_beta`, pulsar `Cerrar proyecto`, verificar vuelta al workspace. | Validado por prueba automatizada. |
| POC-12B: pulsar `Eliminar archivo` tras cerrar proyecto y verificar bloqueo sin proyecto. | Validado por prueba automatizada con el mensaje esperado. |
| POC-12C: iniciar sin proyecto y verificar `Proyecto activo: ninguno`. | Cubierto por inicialización del estado del árbol en pruebas de GUI. |
| POC-12D: abrir `proyecto_beta` y verificar `Proyecto activo: proyecto_beta`. | Cubierto por actualización de estado del proyecto activo en pruebas de GUI. |
| POC-13A: `Eliminar archivo` no borra en primera pulsación. | Validado por prueba automatizada. |
| POC-13B: `Eliminar archivo` borra en segunda pulsación si la ruta no cambia. | Validado por prueba automatizada. |
| POC-13C: `Eliminar carpeta` no borra en primera pulsación. | Validado por prueba automatizada. |
| POC-13D: `Eliminar proyecto` exige confirmación. | Validado por prueba automatizada. |
| POC-13E: siguen funcionando bloqueos contra `../`, `workspace_root` y `project_root`. | Validado por pruebas automatizadas de guardas de ruta y eliminación segura. |

## Desviaciones registradas antes de aceptar el cambio

- No se detectaron desviaciones funcionales en la suite focalizada ejecutada.
- Desviación de entorno: no hay sesión gráfica interactiva disponible en el contenedor, por lo que los clics manuales reales sobre Flet quedan documentados como pendientes de validación humana local.
- Desviación de entorno: no existe `.venv/bin/python`; se usó el intérprete `python` disponible en el contenedor.

## Cobertura automatizada ejecutada como apoyo

Se ejecutó la suite focalizada de GUI/runtime que cubre las garantías críticas del checklist cuando la GUI no puede manipularse manualmente en el contenedor:

```bash
python -m pytest tests/unit/test_gui_idle.py tests/gui/test_idle_path_guards.py tests/gui/test_runtime_delete_safe.py tests/gui/test_auto_suggestion_parser_contract.py tests/gui/test_runtime_correccion_tipografica.py
```

Resultado: `70 passed, 1 warning`.
