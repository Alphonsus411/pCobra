# Hoja de ruta de remediación MyPy

> **Estado:** propuesta de mantenimiento; no modifica la configuración de CI ni
> el contrato del lenguaje.
>
> Esta hoja de ruta organiza la reducción de deuda de tipos de Python en
> pCobra. No sustituye al Libro de Programación Cobra ni autoriza cambios en
> Lexer, Parser, AST, gramática, tokens, aliases, sintaxis Cobra, snapshots,
> fixtures o ejemplos contractuales.

## 1. Motivo y evidencia de partida

`make lint` ejecuta `mypy src/pcobra`, y `make typecheck` lo vuelve a ejecutar
antes de invocar Pyright. Ambos mandatos forman parte de los workflows de CI.
La deuda, por tanto, bloquea tanto el lint como el typecheck globales.

Las auditorías conservadas registran resultados globales de MyPy de la misma
familia de configuración:

| Evidencia | Resultado registrado |
| --- | --- |
| `docs/auditorias/reconciliacion_refs_y_certificacion_pre_merge_2026-08-25/README.md` | 1.750 errores en 270 archivos; 461 ficheros comprobados |
| `docs/auditorias/certificacion_final_grafo_y_merge_2026-08-26/README.md` | 1.754 errores en 273 archivos; 475 ficheros comprobados |
| ejecución de CI observada en la línea actual (octubre de 2026) | 1.725 errores en 270 archivos; 466 ficheros comprobados |

Estas cifras son indicadores históricos, no un baseline inmutable. Cada fase
de trabajo debe volver a medir sobre el SHA exacto que pretende modificar.

## 2. Principios no negociables

1. **MyPy global se conserva.** No se desactiva `make lint`, `make typecheck`,
   ni el paso de CI que los ejecuta.
2. **No se oculta deuda.** Quedan prohibidos `continue-on-error`, exclusiones
   nuevas de código productivo, `follow_imports = skip`,
   `ignore_missing_imports` global adicional, `# type: ignore` sin código y
   justificación, y conversiones masivas a `Any`.
3. **Una familia por PR.** Cada corrección será pequeña, reversible y limitada
   a un grupo coherente de módulos; no se mezcla con POO, runtime,
   transpiladores funcionales, dependencias ni formato general.
4. **Frontera del lenguaje protegida.** Lexer, Parser, AST, gramática y los
   contratos textuales del Libro permanecen fuera de alcance. Cualquier
   excepción requiere autorización explícita y específica antes de editar.
5. **El tipado no cambia ejecución.** Las correcciones deben ser anotaciones,
   `Protocol`, `TypedDict`, `TypeAlias`, tipos de retorno, estrechamiento de
   uniones o stubs. Si un diagnóstico revela un defecto de comportamiento, se
   detiene esa PR y se abre una tarea funcional separada.
6. **La configuración es sensible.** Toda modificación de workflows, de
   `pyproject.toml`, de protección de ramas o de requisitos de checks exige una
   decisión y autorización separadas.

## 3. Secuencia de trabajo

### MYPY-001 — Inventario reproducible (solo lectura)

**Objetivo:** fijar el punto de partida verificable sin cambiar código ni CI.

- Registrar SHA de `master`, versión de Python, versión de MyPy y bloque
  `[tool.mypy]` efectivo.
- Ejecutar el mandato canónico `python -m mypy src/pcobra` en un entorno
  reproducible y guardar, como evidencia de la tarea, el resumen y los
  diagnósticos normalizados por ruta y código.
- Clasificar por prefijo de módulo y código de error, sin inferir que un error
  pertenece al Core únicamente por una dependencia importada.
- Comparar contra las auditorías de §1 y publicar el inventario de ficheros
  sensibles que no se podrán tocar en las fases ordinarias.

**Salida:** baseline fechado y una lista priorizada. No se edita
`pyproject.toml`, Makefile ni workflows.

### MYPY-002 — Triage y orden de dependencias (solo documentación)

**Objetivo:** convertir el inventario en lotes que no mezclen capas.

Los grupos se ordenarán tras el inventario, con esta separación inicial:

| Grupo | Alcance permitido | Riesgo |
| --- | --- | --- |
| Fundaciones de tipos | aliases, protocolos y stubs compartidos | bajo |
| Adaptadores e importaciones de terceros | límites de librerías opcionales y stubs | bajo-medio |
| CLI y utilidades | comandos y presentación, sin contratos Cobra | medio |
| Validadores de biblioteca estándar | validación Python, con pruebas dirigidas | medio |
| Transpiladores | anotaciones internas, sin cambiar salida generada | alto |
| Core | intérprete y límites de AST; Lexer/Parser excluidos | alto |
| Lexer, Parser y AST | excluidos hasta autorización específica | crítico |

Cada lote debe especificar: rutas exactas, número de diagnósticos de partida,
códigos MyPy afectados, pruebas focales y propietario de las decisiones
contractuales cuando exista duda.

**Salida:** lista de PRs candidatas; no se corrige código todavía.

### MYPY-003 — Fundaciones de tipos y dependencias opcionales

**Objetivo:** retirar errores de bajo riesgo que desbloqueen a otros paquetes.

- Introducir solo definiciones de tipo reutilizables y stubs de dependencia
  cuando describan interfaces ya usadas en tiempo de ejecución.
- Preferir `Mapping`, `Sequence`, `Protocol` y uniones explícitas a `Any`.
- Verificar MyPy sobre las rutas del lote, sus pruebas unitarias y el inventario
  global para probar que el total no aumenta.

**Criterio de parada:** cualquier cambio de importación que altere carga en
tiempo de ejecución o comportamiento opcional se separa como incidencia
funcional.

### MYPY-004 — CLI y utilidades ordinarias

**Objetivo:** anotar fronteras de entrada/salida que no formen parte del
lenguaje Cobra.

- Añadir retornos, tipos de colecciones y estrechamiento de valores nulos.
- Mantener mensajes, códigos de salida y formatos de CLI byte a byte.
- Ejecutar pruebas de los comandos afectados y sus contratos de esquema.

**Criterio de parada:** cualquier cambio observado de salida, excepción o
comando requiere una tarea funcional independiente.

### MYPY-005 — Validadores y contratos de biblioteca estándar

**Objetivo:** tipar validadores sin relajar sus reglas de aceptación o rechazo.

- Corregir anotaciones de entradas externas y resultados validados.
- Conservar mensajes de diagnóstico y fixtures existentes.
- Ejecutar pruebas de validadores, contratos de runtime relacionados y MyPy
  focal.

**Criterio de parada:** si se necesita cambiar un contrato textual o un fixture,
no se modifica automáticamente.

### MYPY-006 — Transpiladores, un backend por lote

**Objetivo:** resolver tipado interno sin modificar el código generado.

- Una sola ruta de destino por PR (Python, JavaScript o Rust).
- Comparar las salidas generadas y ejecutar las pruebas contractuales del
  backend antes y después.
- No reordenar, reformatear ni cambiar snapshots como efecto secundario.

**Criterio de parada:** una diferencia de salida, AST o diagnóstico Cobra no es
una corrección de MyPy y debe escalarse.

### MYPY-007 — Core no sintáctico

**Objetivo:** tratar el Core restante que no sea Lexer, Parser ni AST.

- Requiere autorización explícita por grupo de rutas antes de editar.
- Mantener hashes o una revisión de diff dedicada de Lexer, Parser y AST para
  demostrar que no cambiaron.
- Ejecutar smoke sintáctico, pruebas de runtime y contratos POO relevantes,
  además de MyPy focal.

**Criterio de parada:** todo diagnóstico que fuerce una modificación de la
representación sintáctica o semántica pasa a una tarea de lenguaje separada.

### MYPY-008 — Aplicación continua sin ocultar el baseline

**Objetivo:** impedir que la deuda vuelva a crecer mientras se reduce.

Antes de cambiar CI se propondrá por separado un diseño de guardia incremental
que compare contra un baseline versionado, conserve la ejecución global y
publique el total completo. Su objetivo sería rechazar diagnósticos nuevos, no
declarar verde una deuda antigua.

No se implementará esa guardia sin autorización específica: afecta a la señal
de CI y debe revisarse junto con las reglas de ramas. La meta sigue siendo
eliminar el baseline, no perpetuarlo.

### MYPY-009 — Cierre

La restauración de un gate global plenamente verde exige evidencia simultánea:

- `python -m mypy src/pcobra` termina sin errores;
- `make lint` y `make typecheck` terminan sin errores, incluido Pyright si está
  instalado en el entorno de CI;
- las pruebas, smoke sintáctico y contratos de runtime relevantes siguen
  pasando;
- no quedan exclusiones, ignores ni baselines temporales injustificados;
- `git diff --check` y la revisión completa de cada PR no muestran cambios
  funcionales no planificados.

Solo entonces se podrá proponer simplificar o retirar cualquier guardia
transitoria. Cambios administrativos de GitHub siguen requiriendo autorización
propia.

## 4. Plantilla obligatoria para cada PR de remediación

Cada PR debe declarar, como mínimo:

1. SHA de `master` usado y estado limpio del árbol antes de editar.
2. Rutas incluidas y excluidas; confirmación explícita de que no toca Lexer,
   Parser, AST, Libro, snapshots ni fixtures, salvo autorización adjunta.
3. Número y códigos de diagnósticos MyPy antes/después para el lote y para la
   ejecución global.
4. Pruebas focales ejecutadas, resultado de `git diff --check` y revisión del
   diff completo.
5. Cualquier diferencia histórica separada de una posible regresión nueva.
6. Riesgo residual y criterio exacto para detener o escalar la siguiente fase.

## 5. Decisión inmediata

La siguiente acción permitida es **MYPY-001**, exclusivamente de lectura. No
debe iniciarse una corrección de tipos ni una modificación de CI hasta disponer
del inventario reproducible y de autorización para el lote concreto.
