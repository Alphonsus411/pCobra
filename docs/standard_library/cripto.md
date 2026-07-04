# `standard_library.cripto`

## Checklist funcional (cripto)

- [x] Exportaciones canónicas en español via `__all__` únicamente.
- [x] Semántica alineada al runtime de Cobra (validaciones y tipos de retorno).
- [x] Sin alias en inglés expuestos por wildcard export.
- [x] Ejemplo de uso con `usar "cripto"`.

### Ejemplo Cobra

```cobra
usar "cripto"
# invoca funciones públicas del módulo
```

# `standard_library.cripto`

## Criptografía práctica

Ayudantes de uso común para generar tokens, calcular resúmenes y comparar secretos sin filtraciones triviales.

## API pública principal

- `token_seguro(longitud=32)`
- `hash_sha256(datos)`
- `hash_sha512(datos)`
- `comparar_seguro(a, b)`

## Uso rápido

```cobra
usar "cripto"
```

Nombres públicos en español (fuente prevista: `__all__`).

## Nota de seguridad

Los tokens deben generarse con fuentes criptográficamente seguras y las comparaciones de secretos deben usar comparación segura para reducir filtraciones por temporización.
