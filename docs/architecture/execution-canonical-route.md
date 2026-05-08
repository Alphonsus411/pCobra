# Ruta canónica de ejecución y shims de compatibilidad

## Resumen ejecutivo

La **ruta canónica de ejecución** del proyecto se mantiene en `pcobra.core.*` (implementación real), mientras que la CLI pública y el ecosistema moderno consumen `pcobra.cobra.*` como **fachada estable**.

En términos prácticos:

- Implementación de referencia: `pcobra.core`.
- Entrypoints preferidos para CLI: `pcobra.cobra`.
- Compatibilidad retro: módulos shim explícitos que reexportan desde la implementación canónica.

## Inventario de módulos críticos duplicados

### 1) Interpreter

- Canónico: `src/pcobra/core/interpreter.py`
- Shim/adapter: `src/pcobra/cobra/core/interpreter.py`
- Estado: **compatibilidad explícita** (sin lógica propia en el shim).

### 2) Parser

- Canónico de importación pública CLI: `src/pcobra/cobra/core/parser.py`
- Shim/adapter: `src/pcobra/core/parser.py`
- Estado: **compatibilidad explícita**.

### 3) Lexer

- Canónico de importación pública CLI: `src/pcobra/cobra/core/lexer.py`
- Shim/adapter: `src/pcobra/core/lexer.py`
- Estado: **compatibilidad explícita**.

### 4) Runtime

- Entrypoint canónico CLI: `src/pcobra/cobra/core/runtime.py`
- Implementación efectiva: `InterpretadorCobra` en `src/pcobra/core/interpreter.py`.
- Estado: **fachada canónica para CLI** + implementación central reutilizada.

### 5) Import utils

- Canónico de implementación: `src/pcobra/core/import_utils.py`
- Shim/adapter: `src/pcobra/cobra/core/import_utils.py`
- Estado: **compatibilidad explícita**.

## Política oficial

1. Las nuevas integraciones de CLI deben importar desde `pcobra.cobra.*`.
2. Las implementaciones de bajo nivel (núcleo semántico/ejecución) residen en `pcobra.core.*` cuando ya son la fuente de verdad.
3. Todo módulo de compatibilidad debe ser un shim explícito sin lógica de negocio adicional.
4. Cualquier divergencia de comportamiento entre entrypoints (`pcobra.core.*` vs `pcobra.cobra.*`) se considera regresión.

## Contrato mínimo de paridad

Se valida una paridad mínima de:

- Sintaxis/semántica de `usar` entre entrypoints equivalentes.
- Política de exportación (`__all__`) y rechazo de símbolos privados en módulos oficiales.

Esta paridad se prueba en tests de integración para evitar deriva silenciosa entre rutas canónicas y de compatibilidad.
