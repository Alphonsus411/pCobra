# Plan de implementación por tiers de transpilación (pCobra)

## Objetivo
Reducir y estabilizar los targets de transpilación de pCobra en dos niveles:

- **Tier 1:** Python, Rust, JavaScript, WASM.
- **Tier 2:** Go, C++, Java, Ensamblador.

## Tareas estructuradas

### Tarea 1 — Congelar el contrato de targets soportados
- [x] Actualizar el registro único de transpiladores (`TRANSPILERS`) para exponer solo los 8 targets aprobados.
- [x] Sincronizar `LANG_CHOICES` con ese registro.
- [x] Publicar una política explícita de compatibilidad por tier en documentación técnica y de usuario.

### Tarea 2 — Retirar código de backends fuera de alcance
- [x] Eliminar implementaciones `to_*` que no pertenecen a Tier 1/2.
- [x] Eliminar nodos específicos (`*_nodes`) de backends retirados.
- [x] Ejecutar auditoría final de imports para garantizar ausencia total de referencias obsoletas en código de producción.

### Tarea 3 — Asegurar compatibilidad con Holobit SDK y librerías base
- [x] Mantener intactos los transpiladores soportados que ya emiten construcciones `holobit`.
- [x] Conservar flujo de validación de dependencias (`validar_dependencias`) en `compilar`.
- [x] Añadir pruebas de regresión para `holobit`, `graficar`, `proyectar`, `transformar`, `corelibs` y `standard_library` en Tier 1 y Tier 2 (suite dedicada en `tests/integration/transpilers/`).

### Tarea 4 — Limpiar y alinear pruebas
- [x] Retirar tests unitarios/integración de backends eliminados.
- [x] Reescribir matrices de pruebas para clasificar por Tier 1/Tier 2.
- [x] Añadir pipeline de smoke tests mínimo para los 8 targets soportados (incluido en CI al ejecutarse `pytest` sobre `tests/unit`).

### Tarea 5 — Actualizar documentación pública
- [x] Actualizar secciones principales del README (ES/EN) con la nueva lista de destinos.
- [x] Ajustar ejemplos de importación de transpiladores a los 8 soportados.
- [x] Revisar documentación secundaria y ejemplos históricos para eliminar menciones residuales.

## Criterios de aceptación
1. El comando `cobra compilar --tipo` solo acepta los 8 targets de Tier 1/2.
2. No existen módulos `to_*` de lenguajes fuera de alcance en el árbol de código principal.
3. Los tests de compilación/transpilación de targets soportados pasan en CI.
4. README y documentación principal no anuncian destinos fuera de Tier 1/2.


## Matriz mínima garantizada (Tier 1 / Tier 2)

> Esta matriz define el **mínimo contractual** que se valida por pruebas de regresión para cada backend.

| Backend | Tier | holobit(...) | proyectar(...) | transformar(...) | graficar(...) | `corelibs` | `standard_library` |
|---|---|---|---|---|---|---|---|
| Python | Tier 1 | ✅ Completo | ✅ Completo | ✅ Completo | ✅ Completo | ✅ Completo | ✅ Completo |
| JavaScript | Tier 1 | ✅ Completo | ✅ Completo (hook `cobra_proyectar`) | ✅ Completo (hook `cobra_transformar`) | ✅ Completo (hook `cobra_graficar`) | 🟡 Parcial (runtime JS nativo) | 🟡 Parcial (según mapeo) |
| Rust | Tier 1 | 🟡 Parcial (emisión `holobit`) | 🟡 Parcial (hook `cobra_proyectar`) | 🟡 Parcial (hook `cobra_transformar`) | 🟡 Parcial (hook `cobra_graficar`) | 🟡 Parcial (passthrough) | 🟡 Parcial (passthrough) |
| WASM | Tier 1 | 🟡 Parcial (comentario IR) | 🟡 Parcial (runtime hook) | 🟡 Parcial (runtime hook) | 🟡 Parcial (runtime hook) | 🟡 Parcial (runtime import/call) | 🟡 Parcial (runtime import/call) |
| Go | Tier 2 | 🟡 Parcial (slice nativo) | 🟡 Parcial (hook `cobraProyectar`) | 🟡 Parcial (hook `cobraTransformar`) | 🟡 Parcial (hook `cobraGraficar`) | 🟡 Parcial (passthrough) | 🟡 Parcial (passthrough) |
| C++ | Tier 2 | 🟡 Parcial (emisión `holobit`) | 🟡 Parcial (hook `cobra_proyectar`) | 🟡 Parcial (hook `cobra_transformar`) | 🟡 Parcial (hook `cobra_graficar`) | 🟡 Parcial (passthrough) | 🟡 Parcial (passthrough) |
| Java | Tier 2 | 🟡 Parcial (array `double[]`) | 🟡 Parcial (hook `cobraProyectar`) | 🟡 Parcial (hook `cobraTransformar`) | 🟡 Parcial (hook `cobraGraficar`) | 🟡 Parcial (passthrough) | 🟡 Parcial (passthrough) |
| ASM | Tier 2 | 🟡 Parcial (IR simbólico) | 🟡 Parcial (comentario/fallback) | 🟡 Parcial (comentario/fallback) | 🟡 Parcial (comentario/fallback) | 🟡 Parcial (`CALL` runtime) | 🟡 Parcial (`CALL` runtime) |


### Estado de integración de suite oficial (CI)
- [x] Suite dedicada para los 8 backends oficiales ubicada en `tests/integration/transpilers/`.
- [x] Casos separados por tier (`test_official_backends_tier1.py` y `test_official_backends_tier2.py`).
- [x] Criterio **full** aplicado con asserts estrictos de símbolos/hooks/imports esperados.
- [x] Criterio **partial** aplicado con asserts de fallback explícito y no-rotura de generación.
- [x] Validación en CI al ejecutarse `pytest tests` dentro de los workflows (`test.yml`/`ci.yml`).

### Cobertura de regresión asociada

Se añade una suite dedicada que cubre:

1. Importación de cada transpilador oficial (`to_python`, `to_js`, `to_rust`, `to_wasm`, `to_go`, `to_cpp`, `to_java`, `to_asm`).
2. Generación mínima de código por backend para detectar roturas por dependencias.
3. Casos representativos por backend para:
   - `holobit(...)`
   - `proyectar(...)`
   - `transformar(...)`
   - `graficar(...)`
4. Operación típica de librerías de runtime (`longitud(...)`) en todos los backends donde existe llamada de función.

### Política de interpretación

- En JavaScript, `proyectar/transformar/graficar` se resuelven mediante hooks explícitos `cobra_*` inyectados por el transpiler para evitar dependencia implícita de símbolos globales.
- **Tier 1** prioriza estabilidad funcional y cobertura de primitivas Holobit en Python/JS.
- **Tier 2** prioriza continuidad de generación y compatibilidad incremental, con cobertura parcial explícita.
- Cualquier backend fuera de esta matriz se considera fuera de contrato.
