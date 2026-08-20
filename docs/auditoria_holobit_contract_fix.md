# Auditoría de la corrección del contrato público de Holobit

## Problema encontrado

La función pública `graficar` de la corelib declaraba y validaba una salida de
tipo `str`. Esa expectativa era incompatible con el runtime interno: la
operación de graficado se ejecuta por efecto lateral y su retorno normal es
`None`. Como consecuencia, una ejecución interna correcta podía terminar en un
`TypeError` al atravesar la corelib, únicamente porque `None` no satisfacía el
contrato público de texto.

## Solución aplicada

La frontera pública deja de propagar o interpretar el valor devuelto por la
implementación interna. Después de que el adaptador complete la operación sin
excepciones, `graficar` construye y retorna exactamente:

```json
{"estado": "ok"}
```

Antes de entregarlo, el resultado pasa por la validación JSON-safe de la
corelib. El retorno interno se descarta deliberadamente: tanto el `None`
esperado como cualquier otro objeto que pudiera devolver el SDK permanecen
detrás del adaptador y no alteran ni contaminan la respuesta pública.

## Archivos modificados

El cambio mínimo realizado en esta tarea de documentación modifica únicamente:

- `docs/auditoria_holobit_contract_fix.md` (este informe).

No se realizaron cambios adicionales al runtime, a pruebas ni a otros
documentos durante esta tarea.

## Tests ejecutados

Se ejecutaron realmente los siguientes comandos desde la raíz del repositorio:

1. `pytest -q tests/unit/test_holobit_graficar_contract.py tests/unit/test_corelibs_holobit_adapter.py`
   - Resultado: **21 passed in 2.42s** (código de salida 0).
2. `pytest -q tests/integration/test_runtime_python.py`
   - Resultado: **3 passed, 5 warnings in 2.52s** (código de salida 0).
   - Las cinco advertencias son `DeprecationWarning` por el uso compatible de
     `ast.Str` en `src/pcobra/core/sandbox.py`; no representan fallos de estas
     pruebas.

## Riesgos pendientes

- La proyección y las operaciones completas de Holobit en el runtime Python
  siguen dependiendo de `holobit_sdk`.
- Los objetos, las excepciones y los módulos de `holobit_sdk` permanecen detrás
  del adaptador interno: no forman parte del retorno público de `graficar` ni se
  exponen a través de él.
- Una indisponibilidad o un fallo del SDK todavía puede impedir la operación;
  la frontera pública debe continuar traduciendo ese fallo sin filtrar detalles
  internos.

## Confirmación de alcance

Se confirma expresamente que en esta tarea **no fueron modificados** el lexer,
el parser, el AST, los transpiladores, `PUBLIC_API_HOLOBIT` ni `__all__`.
