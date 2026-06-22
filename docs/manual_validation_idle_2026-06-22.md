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

## Checklist manual solicitado

Estos son los pasos que deben validarse en una sesión gráfica interactiva local:

- [ ] Abrir `proyecto_beta`.
- [ ] Abrir `src\principal.cobra`.
- [ ] Ejecutar código.
- [ ] Ver tokens.
- [ ] Ver AST.
- [ ] Obtener sugerencias del Libro con código válido.
- [ ] Aplicar corrección no destructiva con código válido.
- [ ] Comprobar bloqueo de sugerencias/corrección con código inválido.
- [ ] Cerrar proyecto.
- [ ] Intentar operación de archivo sin proyecto activo.
- [ ] Crear proyecto temporal.
- [ ] Eliminar archivo con doble confirmación.
- [ ] Eliminar carpeta con doble confirmación.
- [ ] Eliminar proyecto con confirmación.
- [ ] Comprobar que no se puede borrar `workspace_root`.
- [ ] Comprobar que no se puede borrar `project_root` mediante “Eliminar carpeta”.
- [ ] Comprobar que escapes con `../` siguen bloqueados.

## Cobertura automatizada ejecutada como apoyo

Se ejecutó la suite focalizada de GUI/runtime que cubre las garantías críticas del checklist cuando la GUI no puede manipularse manualmente en el contenedor:

```bash
python -m pytest tests/gui/test_idle_path_guards.py tests/gui/test_runtime_delete_safe.py tests/gui/test_auto_suggestion_parser_contract.py tests/gui/test_runtime_correccion_tipografica.py
```

Resultado: `32 passed, 1 warning`.
