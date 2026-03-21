# Matriz de transpiladores

Este documento resume el **contrato mínimo vigente** de los backends oficiales. No es una promesa de cobertura completa del AST ni de paridad de ejecución entre todos los destinos.

## Fuente de verdad y trazabilidad

La referencia primaria está en estos archivos:

- `src/pcobra/cobra/transpilers/targets.py`: lista canónica de backends y tiers.
- `src/pcobra/cobra/transpilers/registry.py`: registro oficial de clases de transpilador.
- `src/pcobra/cobra/transpilers/compatibility_matrix.py`: matriz contractual por backend/feature.
- `src/pcobra/cobra/transpilers/module_map.py`: resolución canónica de mapeos por backend desde `cobra.toml`.
- `src/pcobra/cobra/cli/target_policies.py`: separación entre targets de transpilación y targets con runtime oficial.
- `src/pcobra/core/sandbox.py`: alcance real de ejecución en sandbox/contenedor.

## Garantía mínima por backend (Tier 1 / Tier 2)

| Backend | Tier | holobit | proyectar | transformar | graficar | corelibs | standard_library |
|---|---|---|---|---|---|---|---|
| `python` | Tier 1 | ✅ full | ✅ full | ✅ full | ✅ full | ✅ full | ✅ full |
| `javascript` | Tier 1 | ✅ full | ✅ full | ✅ full | ✅ full | 🟡 partial | 🟡 partial |
| `rust` | Tier 1 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `wasm` | Tier 1 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `go` | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `cpp` | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `java` | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |
| `asm` | Tier 2 | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial | 🟡 partial |

> `full`: contrato de generación y símbolos/hooks cubierto por regresión.
>
> `partial`: el backend genera código y conserva hooks/fallbacks esperados, pero puede requerir runtime externo o terminar en error controlado.

## Lectura correcta del contrato

### Holobit

- `python` es el único backend documentado hoy como `full` de punta a punta en la matriz.
- `javascript` mantiene contrato `full` para las primitivas Holobit, pero eso **no** implica que todo el runtime auxiliar sea `full`.
- `rust`, `wasm`, `go`, `cpp`, `java` y `asm` deben leerse como soporte contractual **parcial**: el backend emite código, hooks y/o fallbacks verificables; no promete equivalencia total de ejecución.

### `corelibs` y `standard_library`

La compatibilidad mínima exigida por la suite contractual consiste en mantener imports/includes/puntos de llamada verificables en el código generado:

- `python`: imports Python explícitos.
- `javascript`: imports del runtime JS nativo `./nativos/...`.
- `rust`: `use crate::corelibs::*;` y `use crate::standard_library::*;`.
- `wasm`: puntos de llamada WAT y administración externa del runtime.
- `go`: imports `cobra/corelibs` y `cobra/standard_library`.
- `cpp`: includes `cobra/corelibs.hpp` y `cobra/standard_library.hpp`.
- `java`: imports `cobra.corelibs.*` y `cobra.standard_library.*`.
- `asm`: puntos de llamada `CALL` al runtime externo.

## Relación entre transpilación y runtime

Los 8 backends son oficiales para **generación de código**, pero el tooling oficial de **ejecución** es más pequeño:

- runtime oficial en contenedor/sandbox: `python`, `javascript`, `cpp`, `rust`.
- targets oficiales solo de transpilación: `wasm`, `go`, `java`, `asm`.
- verificación ejecutable explícita en CLI: `python`, `javascript`.

Además:

- el runtime JavaScript depende del entorno (`node`, `vm2` y, para ciertas pruebas, `node-fetch`);
- `holobit-sdk` está declarado en `pyproject.toml` como dependencia condicionada a Python `>=3.10`.

## Qué valida realmente la batería actual

La cobertura contractual actual se apoya en:

- `tests/integration/transpilers/test_official_backends_tier1.py`
- `tests/integration/transpilers/test_official_backends_tier2.py`
- `tests/integration/transpilers/test_official_backends_contracts.py`
- `tests/integration/test_holobit_tiers.py`
- `tests/unit/test_holobit_backend_contract_matrix.py`
- `tests/unit/test_official_targets_consistency.py`

Estas suites verifican, como mínimo:

1. que los 8 backends oficiales generan salida;
2. que el nivel declarado en la matrix coincide con símbolos/hooks/fallbacks esperados;
3. que la forma del contrato no se desalineó del mínimo requerido;
4. que la política pública no reintroduce aliases o targets fuera de alcance.

La mera existencia de esta batería no debe leerse como garantía de verde permanente: precisamente estas suites son las que detectan los desajustes cuando la implementación real no coincide con el contrato documentado.

## Criterios verificables sugeridos

```bash
python scripts/ci/validate_targets.py
python -m pytest tests/unit/test_official_targets_consistency.py
python -m pytest tests/unit/test_holobit_backend_contract_matrix.py
python -m pytest tests/integration/transpilers/test_official_backends_tier1.py
python -m pytest tests/integration/transpilers/test_official_backends_tier2.py
python -m pytest tests/integration/transpilers/test_official_backends_contracts.py
```

## Nota sobre la antigua “matriz de características del AST”

La tabla histórica de cobertura amplia del AST se elimina de este documento porque inducía a leer como contrato lo que hoy no está respaldado por la batería contractual vigente. Si se quiere recuperar una matriz así, debe derivarse de tests automáticos backend por backend y marcarse explícitamente como **histórica** o **exploratoria**, no contractual.
