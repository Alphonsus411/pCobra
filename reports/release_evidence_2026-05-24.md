# Evidencia de verificación de wheel (2026-05-24)

## Comandos ejecutados
1. `python -m build --wheel`
2. `python -m venv .venv-release-test`
3. `pip install dist/pcobra-10.1.1-py3-none-any.whl`
4. `cobra --version`
5. `python -c "from pcobra.cobra.transpilers.runtime_api_matrix import build_runtime_api_matrix; print(type(build_runtime_api_matrix()).__name__)"`

## Resultados clave
- Wheel construida: `dist/pcobra-10.1.1-py3-none-any.whl`.
- `cobra --version`: **falló** con `RuntimeError` de contrato startup (módulo canónico `numero` faltante en ruta `src/pcobra/corelibs/numero.py`).
- `build_runtime_api_matrix()`: salida `dict`.
