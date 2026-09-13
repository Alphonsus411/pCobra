# Inventario técnico de módulos `usar`

Fecha de actualización: 2026-09-13.

## 1) Contrato público Cobra-facing

### 1.1 Sintaxis: norma y comportamiento observado

El Libro (§3.6) es normativo y publica exclusivamente una cadena después de
`usar`. Sus dos variantes documentadas son una ruta simple (`usar "texto"`) y
una ruta lógica punteada dentro de la cadena (`usar "mi_modulo.utilidades"`).

La cadena completa comprobada en la implementación es:

1. `PALABRAS_RESERVADAS` incluye `usar`.
2. `Lexer` reconoce `usar` como `TipoToken.USAR`; `tokenizar()` delega en la
   tokenización base (salvo los modos incremental o de perfilado).
3. `Parser.declaracion_usar()` consume directamente un token `CADENA`, o bien
   construye una ruta con dos o más tokens `IDENTIFICADOR` separados por
   `PUNTO`, y produce en ambos casos `NodoUsar(modulo: str)`.

Por tanto, las formas observadas son:

| Fuente Cobra | Parser | Estado contractual |
|---|---|---|
| `usar "texto"` | acepta `NodoUsar("texto")` | normativa |
| `usar "utilidades.fechas"` | acepta `NodoUsar("utilidades.fechas")` | normativa |
| `usar utilidades.fechas` | acepta `NodoUsar("utilidades.fechas")` | compatibilidad observada, no publicada por el Libro |
| `usar texto` | rechaza | un identificador simple exige comillas |

Este inventario caracteriza la rama existente sin convertir la ruta punteada
sin comillas en sintaxis normativa ni proponer aliases o gramática adicional.

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
- El intérprete entrega `NodoUsar.modulo` a la API única `usar_modulo`, inyecta
  únicamente los símbolos saneados en el ámbito plano y conserva su metadata
  para auditoría. El cargador distingue módulos oficiales simples de módulos
  Cobra de proyecto con ruta lógica punteada; `usar_policy.py` mantiene el
  catálogo/capacidades y `usar_symbol_policy.py` filtra nombres y valida la
  metadata de cada export antes de exponerlo.

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
