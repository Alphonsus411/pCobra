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

## 5) Contrato canónico de exports públicos por módulo

Para evitar exposición accidental de internals, el contrato de exportación pública de módulos canónicos de `usar` se define y verifica en tres capas:

1. **Contrato por módulo**: cada módulo canónico en `src/pcobra/corelibs/` y su espejo en `src/pcobra/standard_library/` declara `__all__` explícito.
2. **Snapshot canónico**: `tests/data/usar_exports_snapshot.json` fija (por módulo) el set exacto y orden contractual de exports públicos.
3. **Pruebas anti-deriva**: `tests/test_usar_public_exports_snapshot.py` falla cuando:
   - aparece un símbolo interno (prefijo `_`),
   - aparece un símbolo runtime prohibido por contrato,
   - falta cualquier símbolo contractual obligatorio (funciones requeridas o aliases permitidos),
   - cambia el snapshot (set u orden).

Con esto, cualquier deriva en la superficie pública de `usar` queda bloqueada en CI.
