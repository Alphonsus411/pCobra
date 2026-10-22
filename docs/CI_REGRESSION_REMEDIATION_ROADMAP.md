# Hoja de ruta de bloqueos de CI y posibles regresiones

> **Estado:** propuesta de diagnóstico y remediación incremental.
>
> **Alcance:** separa fallos globales de CI de una posible regresión de una PR.
> No autoriza cambios en Lexer, Parser, AST, gramática, tokens, aliases,
> sintaxis Cobra, Libro de Programación, snapshots, fixtures ni ejemplos.
> Tampoco autoriza cambiar la configuración de GitHub, protecciones de rama,
> permisos, credenciales o CodeQL.

## 1. Evidencia que origina esta lista

- **Base:** `master` en `68e0465d3793078f2c7763f1e51f7748eb8e9f60`.
- **PR observada:** #3805, cabeza
  `8ececac55f29384c8fd723adcb006f9bcfcb88e2`.
- **Alcance de la PR:** `src/pcobra/gui/idle.py` y
  `tests/gui/test_idle_packaging.py`; no cambia componentes protegidos.
- **Comprobaciones correctas:** Lint, Runtime Stabilization Contract, gate
  contractual, prueba focal Rust y dependencias de ruedas para Python
  3.11--3.13.
- **Comprobaciones bloqueadas:** MyPy global, benchmark de releases y CodeQL.

La PR elimina los accesos a `IdlePackageResult.output_dir` y
`IdlePackageResult.artifact_path`, atributos que no forman parte del contrato
publicado por `idle_bridge`. Las pruebas focales locales de empaquetado y puente
IDLE pasaron (10 pruebas). El log de CI no contiene ya esos dos diagnósticos.

Los fallos restantes se consideran **deuda global o configuración** hasta que
una comparación sobre el mismo SHA de base pruebe lo contrario. No se permite
fusionar ignorándolos.

## 2. Clasificación inicial

| ID | Hallazgo | Tipo | Evidencia actual | Riesgo de regresión de #3805 |
| --- | --- | --- | --- | --- |
| REG-001 | Contrato de resultado del empaquetado IDLE | Corrección funcional focal | dos atributos inexistentes eliminados; pruebas focales correctas | bajo, pendiente de CI que alcance pytest |
| CI-001 | MyPy global | Deuda histórica medible | 1.701 errores, 253 ficheros, 466 comprobados | no atribuible con la evidencia actual |
| CI-002 | Benchmark invoca `compilar` | Incompatibilidad de integración | CLI expone `run`, `build`, `test`, `mod`, `repl`, `gui` | no relacionada con #3805 |
| CI-003 | Benchmark no encuentra release base | Dependencia externa o baseline roto | API de releases devuelve HTTP 404 | no relacionada con #3805 |
| CI-004 | CodeQL doble modalidad | Configuración administrativa | default setup y análisis avanzado activos a la vez | no relacionada con #3805 |
| CI-005 | CodeQL intenta analizar ficheros `.git` | Posible endurecimiento pendiente | diagnósticos de parseo en refs/logs de Git | no tratar antes de resolver CI-004 |
| CI-006 | Jobs Windows cancelados | Efecto de fallo previo | cancelación posterior al fallo Ubuntu | no es un fallo independiente sin reejecución verde |

## 3. Reglas de ejecución

1. Una tarea por rama y PR; no se inicia la siguiente automáticamente.
2. Antes de editar: registrar SHA exacto de `master`, árbol limpio, rutas
   previstas y pruebas. Si la base cambia, repetir la clasificación.
3. Después de editar: ejecutar pruebas focales, `git diff --check`, revisar
   diff completo y confirmar explícitamente que no se tocó Lexer, Parser ni
   AST.
4. No se añaden exclusiones de MyPy, `continue-on-error`, ignores masivos ni
   se relajan umbrales para volver verde un check.
5. Si aparece una modificación semántica, de CLI pública, de mensaje
   contractual, de fixture o de salida generada, parar y abrir una incidencia
   funcional separada.
6. Cualquier ajuste de CodeQL default setup, permisos, protección de ramas o
   configuración administrativa de GitHub requiere autorización específica
   previa y no se realiza desde una tarea de código.

## 4. Secuencia propuesta

### REG-001A — Certificar el contrato IDLE en la rama de la PR

**Objetivo:** distinguir la corrección de empaquetado de los bloqueos globales.

- Repetir en el SHA de #3805: pruebas de `test_idle_packaging.py` y
  `test_cobra_installer_idle_bridge.py`, importación de IDLE y MyPy focal.
- Confirmar que no se informa de `output_dir` ni `artifact_path` en
  `src/pcobra/gui/idle.py`.
- No se modifica código en esta tarea; solo se adjunta evidencia a la PR.

**Salida:** evidencia reproducible de que la corrección funciona de forma
aislada. Si falla, la PR queda bloqueada y se crea una incidencia funcional
específica, sin mezclarla con CI.

### CI-001A — Baseline MyPy comparable

**Objetivo:** obtener una comparación honesta entre `master` y una cabeza de PR.

- Ejecutar el mandato canónico de CI (`mypy src/pcobra` o su equivalente
  exacto de Make) con las mismas versiones de Python y MyPy.
- Normalizar el resultado por ruta y código; registrar total, ficheros y las
  incidencias de `gui/idle.py`.
- Comparar únicamente resultados de la misma configuración y del mismo
  conjunto de ficheros comprobados.

**No editar:** código, `pyproject.toml`, Makefile, workflows o baselines.

**Salida:** clasificación de cada diferencia como nueva, eliminada o histórica.
El tratamiento de deuda seguirá `docs/CI_MYPY_REMEDIATION_ROADMAP.md`.

### CI-001B — Lote GUI de tipos, solo después de CI-001A

**Objetivo:** reducir los diagnósticos residuales de IDLE sin cambiar su
comportamiento.

- Un subgrupo homogéneo por PR: primero retornos y parámetros de callbacks;
  después atributos de Flet o lambdas, nunca juntos.
- Mantener exactamente los mensajes, flujos y controles GUI.
- Ejecutar MyPy focal, pruebas de IDLE y una prueba de regresión del resultado
  de empaquetado.

**Parada obligatoria:** si la anotación requiere adaptar una API de Flet,
cambiar la interacción del usuario o modificar `runtime.py`, abrir una tarea
funcional y pedir autorización de alcance.

### CI-002A — Inventario del contrato del runner de benchmarks

**Objetivo:** demostrar cuál es el comando canónico y dónde se introdujo
`compilar`.

- Localizar el caso de benchmark que emite el comando y contrastarlo contra el
  parser/ayuda pública de la CLI, sin modificarlo.
- Definir una prueba pequeña que ejecute solo ese caso y compruebe código de
  salida, salida JSON y el comando invocado.
- Evaluar si el remedio mínimo es cambiar una llamada del script de benchmark
  o restaurar un contrato de CLI. La segunda opción toca un contrato público y
  no se asume.

**Salida:** propuesta de una corrección de una ruta. No editar Lexer, Parser ni
CLI pública en esta tarea de inventario.

### CI-002B — Reparación mínima del invocador de benchmark

**Precondición:** autorización explícita tras CI-002A.

- Modificar solo el invocador confirmado de benchmark para usar el subcomando
  canónico existente; no se añade alias `compilar` ni se cambia la CLI.
- Añadir o ajustar una única prueba del runner que detecte un subcomando no
  soportado antes de lanzar la comparación completa.
- Ejecutar el runner focal y la comparación cuando exista una base disponible.

**Parada obligatoria:** si el inventario muestra que la sintaxis Cobra o la CLI
pública exige compatibilidad adicional, no aplicar el cambio.

### CI-003A — Diagnóstico de disponibilidad del baseline de benchmark

**Objetivo:** separar un fallo de red/release de un fallo de medición.

- Consultar metadatos de la última release y del artefacto
  `benchmarks.json`, registrando estado HTTP, tag y URL sin descargar ni
  publicar nada.
- Verificar la existencia de la ruta `benchmarks-history` que el workflow
  espera cuando se proporciona `--base`.
- Determinar una fuente de baseline estable y versionada, sin usar una
  release inexistente como señal de regresión.

**Salida:** decisión documentada entre arreglar el publicador de artefactos,
usar un baseline versionado existente o declarar que el benchmark debe quedar
explícitamente bloqueado hasta que exista baseline. No se oculta ni se omite.

### CI-003B — Baseline de benchmark reproducible

**Precondición:** autorización explícita tras CI-003A.

- Implementar una sola estrategia aprobada para obtener el baseline.
- Probar: base presente, base ausente, JSON inválido y comparación correcta.
- Conservar fallo explícito y comprensible si la base no existe; no convertirlo
en éxito silencioso.

### CI-004A — Decisión administrativa de CodeQL

**Objetivo:** resolver el conflicto entre CodeQL default setup y configuración
avanzada sin debilitar análisis de seguridad.

- Presentar las dos alternativas: desactivar default setup en GitHub y
  conservar `.github/workflows/codeql.yml`, o retirar el workflow avanzado y
  migrar todas las consultas necesarias al modo permitido.
- Revisar qué consultas personalizadas y pruebas dependen del workflow
  avanzado actual.

**Parada obligatoria:** esta tarea no modifica nada. Cambiar la modalidad de
CodeQL en GitHub requiere autorización administrativa separada.

### CI-004B — Aplicar la modalidad CodeQL aprobada

**Precondición:** autorización administrativa específica después de CI-004A.

- Aplicar una sola modalidad y ejecutar CodeQL sobre una rama sin cambios de
  lenguaje.
- Verificar que las consultas personalizadas siguen ejecutándose y que el
  análisis se sube correctamente.

### CI-005A — Alcance de análisis de CodeQL

**Precondición:** CI-004B verde.

- Confirmar si los avisos de `.git` persisten tras resolver la modalidad.
- Si persisten, identificar por qué el checkout/consulta los incluye y
  proponer la exclusión mínima que preserve `src`, tests y consultas propias.

**Parada obligatoria:** no añadir exclusiones ni tocar las consultas `.ql`
sin una propuesta revisada y autorización concreta.

### CI-006A — Reejecución de matriz cancelada

**Precondición:** los bloqueos anteriores pertinentes resueltos o aislados.

- Reejecutar la matriz Windows solo cuando Ubuntu complete los pasos previos.
- Clasificar una cancelación como no concluyente; no como éxito ni regresión.

## 5. Criterio de integración de una PR funcional

Una PR como #3805 puede proponerse para integración únicamente cuando:

1. deje de estar en borrador;
2. no haya conflictos con `master`;
3. sus pruebas focales y gates contractuales estén correctos;
4. los checks requeridos estén verdes o exista una decisión explícita,
documentada y aprobada sobre un bloqueo independiente; y
5. el diff siga limitado a su incidencia y no toque componentes protegidos.

Mientras CI-001, CI-002, CI-003 y CI-004 estén abiertos, la integración no se
fuerza y no se ignoran checks.

## 6. Orden inmediato recomendado

1. **REG-001A:** adjuntar y revisar evidencia focal de #3805.
2. **CI-001A:** medir baseline MyPy comparable; no abrir aún otro lote de
   tipos.
3. **CI-002A:** inventariar el origen de `compilar`.
4. **CI-003A:** verificar artefacto/base de benchmarks.
5. **CI-004A:** presentar la decisión administrativa de CodeQL.

Cada punto termina con una decisión explícita antes de iniciar el siguiente.
