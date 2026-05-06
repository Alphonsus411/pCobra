# `standard_library.archivo`

## Checklist funcional (archivo)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "archivo"`.

### Ejemplo Cobra

```cobra
usar "archivo"
# invoca funciones públicas del módulo
```

# `standard_library.archivo`

Documentación sincronizada automáticamente desde `src/pcobra/standard_library/archivo.py`.

<!-- BEGIN: AUTO-STDLIB-FUNCTIONS -->
## API pública sincronizada (`standard_library.archivo`)

| Función |
|---|
| `adjuntar` |
| `escribir` |
| `existe` |
| `leer` |
<!-- END: AUTO-STDLIB-FUNCTIONS -->


## Nuevas utilidades
- `anexar(ruta, datos)`: agrega texto al final de un archivo seguro.
- `leer_lineas(ruta, mantener_saltos=False)`: lee el archivo y separa por líneas.
