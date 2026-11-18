# Roadmap pCobra — Estabilización funcional (#3873 y #3874)

> Estado: **PLANIFICADO** · Versión: 1.0 · Fecha de registro: 2026-11-18  
> Rama documental: `docs/roadmap-issues-3873-3874`  
> Baseline inmutable de referencia: `68e0465d3793078f2c7763f1e51f7748eb8e9f60` (pCobra 10.1.2)

## Objetivo y alcance

Estabilizar `cobra test` y alinear los ejemplos del libro oficial con el lenguaje implementado, con pruebas reproducibles y trazabilidad de la CI. Issues fuente:

- [#3873 — `cobra test` y dependencias de los backends](https://github.com/Alphonsus411/pCobra/issues/3873)
- [#3874 — Ejemplos del libro incompatibles con la ejecución](https://github.com/Alphonsus411/pCobra/issues/3874)

**Alcance acordado:** diagnóstico, regresiones, mejoras acotadas de la CLI si son compatibles con contratos existentes, auditoría ejecutable y correcciones documentales. La ampliación de la gramática se excluye de esta fase.

**Restricciones obligatorias:** no merge ni push adicional automático; no modificar Lexer, Parser, AST, gramática, fixtures ni contratos sin nueva autorización expresa; no relajar/omitir gates ni pruebas; backends oficiales exclusivamente Python, JavaScript y Rust; no Go/Java/JDK/Chocolatey. Toda PR será inicialmente Draft y requerirá evidencia remota antes de decidir una integración.

## Estado de ejecución

| Fase | Peso | Estado | Evidencia / PR |
| --- | ---: | --- | --- |
| F1. Diagnóstico reproducible | 20 % | Pendiente | — |
| F2. `cobra test` (#3873) | 25 % | Pendiente | — |
| F3. Auditoría del libro (#3874) | 20 % | Pendiente | — |
| F4. Correcciones documentales | 15 % | Pendiente | — |
| F5. CI, revisión y cierre | 20 % | Pendiente | — |
| **Total verificado** | **100 %** | **0 %** | Sin evidencia de ejecución aún |

**Regla de cómputo:** una fase solo se marca `[x]` y suma su peso cuando **todos** sus criterios de aceptación cuentan con evidencia enlazada o registrada; trabajos parciales quedan `[ ]` con nota de avance. No confundir issue abierto, PR creada o test local verde con cierre validado.

## Lista de tareas y criterios de aceptación

### F1 — Diagnóstico reproducible (20 %)

- [ ] Confirmar HEAD/baseline y entorno de ejecución usados en pruebas, sin alterar producción.
- [ ] Reproducir #3873 con `cobra run` y `cobra test`, capturando códigos de salida y salidas relevantes.
- [ ] Separar errores del intérprete, RestrictedPython, ausencia de `vm2` y falta de Docker, sin asumir causas no demostradas.
- [ ] Reproducir muestras representativas de #3874 (`funcion`/`retornar`, f-strings, parámetros por defecto, `fin`).
- [ ] Guardar matriz de resultados: comando, entorno, esperado, observado, referencia y clasificación.

**Aceptación:** evidencia repetible de ambos issues y triage sin modificaciones funcionales.  
**Evidencia:** pendiente.

### F2 — Estabilización de `cobra test` (#3873) (25 %)

- [ ] Documentar el contrato actual de `cobra test` y el papel de intérprete y tres backends.
- [ ] Diseñar y validar una separación explícita entre ejecución de programa y comprobación de equivalencia; no declarar verde si faltan dependencias necesarias.
- [ ] Añadir pruebas de regresión para programa trivial, dependencia ausente y error real de backend.
- [ ] Confirmar que no se desactivan los controles de Python, JavaScript ni Rust y que los errores no se silencian.
- [ ] Preparar PR Draft mínima con referencia a #3873 y resultados locales; conservar sin merge.

**Aceptación:** comportamiento definido y comprobable, regresiones relevantes y PR trazable; validación remota requerida en F5.  
**Evidencia:** pendiente.

### F3 — Auditoría ejecutable del libro (#3874) (20 %)

- [ ] Inventariar fragmentos de `docs/LIBRO_PROGRAMACION_COBRA.md` por sección y tipo (ejecutable, parcial, pseudocódigo).
- [ ] Inspeccionar `scripts/ci/audit_reglas_libro_programacion.py` antes de asumir qué comprueba.
- [ ] Ejecutar los ejemplos clasificados como ejecutables en un entorno controlado, documentando requisitos y resultados.
- [ ] Clasificar cada discrepancia: documentación errónea, función no implementada, parser/contrato o dependencia ambiental.
- [ ] Relacionar duplicidades con #3865, #3866 y #3867 sin resolverlos tácitamente.

**Aceptación:** matriz completa de ejemplos clasificados y comprobación reproducible, sin cambios de sintaxis.  
**Evidencia:** pendiente.

### F4 — Correcciones documentales (#3874) (15 %)

- [ ] Alinear ejemplos y palabras reservadas con el comportamiento comprobado, sin inventar soporte.
- [ ] Documentar explícitamente las funciones o sintaxis aún no soportadas.
- [ ] Preservar las secciones que describan aspiraciones de diseño, marcándolas como no implementadas cuando corresponda.
- [ ] Abrir PR Draft documental separada, enlazada a #3874, con alcance mínimo.
- [ ] Comprobar que las modificaciones no introducen ejemplos ejecutables rotos.

**Aceptación:** documentos coherentes con evidencias de ejecución y PR Draft documental trazable.  
**Evidencia:** pendiente.

### F5 — Validación de CI y cierre (20 %)

- [ ] Revisar las ejecuciones de CI ligadas a cada PR (no extrapolar de runs históricos).
- [ ] Verificar matriz Ubuntu/Windows con Python 3.11 y 3.12 cuando los workflows realmente ejecuten esas combinaciones.
- [ ] Revisar gates relevantes (Ruff, Mypy, Bandit, smoke y contratos), sin omisiones ni relajaciones.
- [ ] Distinguir regresiones introducidas de deuda histórica (Mypy, CodeQL, benchmarks u otras) con enlaces a logs.
- [ ] Registrar riesgos residuales, evidencia por PR y decisión recomendada: apta/no apta/pendiente; **no fusionar automáticamente**.
- [ ] Actualizar el estado de #3873/#3874 únicamente cuando la evidencia justifique el cambio.

**Aceptación:** informe de validación verificable, con bloqueo explícito de cualquier PR sin evidencias suficientes.  
**Evidencia:** pendiente.

## Registro cronológico de trazabilidad

| Fecha (UTC) | Evento | Evidencia | Resultado |
| --- | --- | --- | --- |
| 2026-11-18 | Alta del roadmap para #3873 y #3874 | Issues enlazados arriba; baseline `68e0465` | Plan registrado; 0 % ejecutado |

### Plantilla para próximos avances

Añadir una fila al registro y actualizar las casillas **solo después de comprobar**:

```text
AAAA-MM-DD HH:MM UTC | Fase/tarea | rama/commit | entorno y comando | observado/esperado | enlace CI/PR/log | PASS/FAIL/BLOCKED | siguiente acción
```

Cuando falle un gate, registrar **el fallo**; no marcarlo como éxito por ejecutarse. Conservar enlaces a PR, runs y commits; evitar secretos, tokens y datos corporativos.

## Dependencias y política de decisión

- F1 precede a F2 y F3; F3 precede a F4. F5 valida F2 y F4.
- No declarar resuelto #3873 solo porque se puede ejecutar un modo sin backends; documentar la diferencia entre modo intérprete y paridad.
- No declarar resuelto #3874 hasta contrastar ejemplos ejecutables con resultados; la sintaxis nueva requeriría otro ciclo y autorización independiente.
- Las PR de CI y seguridad existentes se tratan como contexto y deuda independiente; este roadmap no autoriza su merge.

**Próximo paso autorizado:** iniciar F1 en modo lectura/diagnóstico y rellenar el registro con resultados verificables.
