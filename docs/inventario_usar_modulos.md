# Inventario técnico de módulos `usar`

Fecha de actualización: 2026-05-03.

## 1) Contrato público Cobra-facing

`usar` **solo** resuelve módulos Cobra-facing canónicos. La fuente única del contrato es:

- `USAR_COBRA_PUBLIC_MODULES` en `src/pcobra/cobra/usar_loader.py`.

La política de REPL (`REPL_COBRA_MODULE_MAP`) se deriva de esa misma constante en `src/pcobra/cobra/usar_policy.py`, evitando listas divergentes.

Módulos canónicos permitidos (orden contractual exacto):

1. `numero`
2. `texto`
3. `datos`
4. `logica`
5. `asincrono`
6. `sistema`
7. `archivo`
8. `tiempo`
9. `red`
10. `holobit`

## 2) Resolución runtime

- `obtener_modulo(nombre, ...)` valida nombre seguro y permite únicamente módulos incluidos en la constante canónica.
- `obtener_modulo_cobra_oficial(nombre)` resuelve desde `corelibs/` o `standard_library/`.
- En REPL estricto, cualquier módulo externo se rechaza.

## 3) Verificación de consistencia

- `scripts/validate_runtime_contract.py` valida que la constante canónica mantiene exactamente el contrato esperado.
- `tests/integration/test_repl_usar_entrypoints_contract.py` verifica que los entrypoints REPL usan la política canónica y que el comportamiento de `usar` mantiene seguridad y atomicidad.

## 4) Alcance de API

No son API pública de `usar`:

- rutas internas de backends,
- símbolos internos de SDK,
- aliases legacy fuera del set canónico.

El contrato estable para usuario final es únicamente la lista canónica Cobra-facing indicada arriba.
