# `standard_library.configuracion`

## Checklist funcional (configuracion)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "configuracion"`.

### Ejemplo Cobra

```cobra
usar "configuracion"
# invoca funciones públicas del módulo
```

# `standard_library.configuracion`

## Configuración de aplicaciones

Carga de configuración estructurada desde archivos y acceso con valores por defecto.

## API pública principal

- `cargar(ruta)`
- `cargar_toml(ruta)`
- `obtener(config, clave, defecto=None)`
- `requerir(config, clave)`

## Uso rápido

```cobra
usar "configuracion"
```

Nombres públicos en español (fuente prevista: `__all__`).

## Nota de seguridad

El soporte TOML depende de `tomllib`; en versiones de Python sin `tomllib` se requiere un backend compatible.
