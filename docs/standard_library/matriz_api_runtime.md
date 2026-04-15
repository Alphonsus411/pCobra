# Matriz viva de API runtime (`corelibs` + `standard_library`)

Este flujo genera un inventario **vivo** de API pública Python y su cobertura por backend.

## ¿Qué extrae?

1. Exports públicos de:
   - `src/pcobra/standard_library/__init__.py` (`__all__`)
   - `src/pcobra/corelibs/__init__.py` (`__all__`)
2. Mapa de paridad por backend desde:
   - `src/pcobra/cobra/transpilers/runtime_api_parity_snapshot.json`

## Salidas

Ejecuta:

```bash
python scripts/generar_matriz_api_runtime.py
```

Se generan:

- `docs/_generated/runtime_api_matrix.json`
- `docs/_generated/runtime_api_matrix.md`
- `docs/_generated/stdlib_contract_matrix.md` (matriz única contractual de módulos `cobra.core|datos|web|system`)
- `docs/_generated/stdlib_contract_matrix.json` (misma matriz en formato consumible por CLI/docs)
- `docs/standard_library/matriz_stdlib_unificada.md` (vista publicada de referencia en docs)

El JSON incluye tres bloques:

- `global_api`: API disponible global (unión + desglose por namespace).
- `available_api_by_backend`: API parcial disponible por backend.
- `missing_api_by_backend`: API faltante por backend.

## Contrato de mantenimiento

Existe un test de contrato (`tests/unit/test_runtime_api_matrix_contract.py`) que valida:

- que el snapshot `python_global_api_snapshot` esté sincronizado con los `__all__` reales;
- que el mapa de paridad cubra todos los backends oficiales.

Si se agrega API en Python sin actualizar el snapshot/mapa, el test falla.

## Contrato de módulos stdlib (descriptores Python)

El contrato público de módulos se define en `src/pcobra/cobra/stdlib_contract/` usando descriptores Python:

- `core.py`
- `datos.py`
- `web.py`
- `system.py`

Para sincronizar manifiestos y documentación generada:

```bash
python scripts/generar_contrato_stdlib.py
```

Este flujo actualiza:

- `src/pcobra/cobra/stdlib_contract/cobra.*` (manifiestos consumidos por `module_map`)
- `docs/_generated/stdlib_contract_matrix.md` (API pública + backend primario + fallback + cobertura `full/partial`)
- `docs/_generated/stdlib_contract_matrix.json` (matriz estructurada para consumo de CLI/docs)
- `docs/standard_library/matriz_stdlib_unificada.md` (publicación única para documentación funcional)
