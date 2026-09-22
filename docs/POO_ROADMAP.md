# Hoja de ruta técnica de POO de pCobra

> **ADVERTENCIA DE GOBERNANZA**
>
> Este documento es la hoja de ruta técnica vinculante para implementar y
> verificar el contrato POO definido en el
> [`Libro de Programación Cobra`](LIBRO_PROGRAMACION_COBRA.md). No sustituye al
> Libro como especificación normativa del lenguaje.
>
> Durante las Tasks 42.x, cualquier implementación POO debe respetar las
> decisiones normativas ya incorporadas al Libro y las restricciones técnicas
> de este Roadmap.
>
> Cualquier agente automático, mantenedor o tarea futura que modifique Lexer,
> Parser, AST, análisis semántico, runtime o backends relacionados con POO
> **DEBE** leer este documento antes de realizar cambios.
>
> No se deben introducir decisiones sintácticas o semánticas incompatibles con
> el Libro. Este documento no es orientativo en cuanto al plan técnico: explica
> cómo implementar y verificar el contrato lingüístico sin desviaciones.

## 1. Trazabilidad y alcance

- **Auditoría origen:** `audit_evidence/phase2/task42_poo_forensics.md`.
- **SHA auditado originalmente:** `f12648682b9a019a10aa3d84e6b285c7d17ca73c`.
- **PR de Task 42:** `#3640`.
- **SHA de inicio de Task 42A:** `7b848fa6cee6d76d8370e09ea84e55bd94243ed1`.

Task 42A fija contrato y planificación; **no implementa reparaciones POO**. Los
estados de esta hoja describen capacidades verificadas, no aspiraciones.

### ALINEACIÓN NORMATIVA TASK 42A.1

La divergencia histórica comprobada era:

```text
Antes:
Libro   → self / __init__
Roadmap → este / inicializar

Después:
Libro   → este / inicializar
Roadmap → implementación de este / inicializar
```

Task 42A.1 resuelve exclusivamente esa contradicción documental y de
gobernanza. No afirma que el código productivo ya esté alineado: los hallazgos
POO y sus pruebas continúan pendientes según la tabla y la secuencia de este
Roadmap. La jerarquía inequívoca es:

```text
AGENTS.md → Libro → contrato normativo del lenguaje
POO_ROADMAP.md     → plan técnico para implementar y verificar ese contrato
```

### ALINEACIÓN DOCUMENTAL TASK 42A.2

Task 42A.1 alineó el Libro con las decisiones `este` e `inicializar`, pero su
revisión posterior detectó dos anticipaciones indebidas de la gramática vigente:
la omisión del `fin` individual de cada método y el uso multiargumento de
`imprimir`. Task 42A.2 devolvió entonces el Libro a los cierres que aceptaba el
Parser antes de 42C, y ajustó el smoke para usar exclusivamente una expresión
soportada por `imprimir`. No cambió ninguna decisión POO
fundamental ni afirma soporte productivo completo.

### ALINEACIÓN DOCUMENTAL TASK 42A.3

Task 42A.1 alineó Libro y Roadmap en `este` e `inicializar`, y Task 42A.2
corrigió la impresión multiargumento y documentó la limitación real del Parser.
La revisión de 42A.2 detectó que incorporar el `fin` por método a la gramática
normativa confundía esa implementación actual con el contrato. Task 42A.3
separa definitivamente **CONTRATO NORMATIVO** de **ESTADO ACTUAL DEL PARSER**:
el primero no contiene cierres individuales de método y el segundo registra que
el Parser todavía los exigía en ese momento. POO-001 quedó resuelto en 42C. Esta alineación
es exclusivamente documental y no modifica código productivo.

## 2. Principio fundamental y frontera neutral

> pCobra posee su propia sintaxis y semántica pública. Python, JavaScript y Rust
> son destinos de transpilación y no deben determinar la sintaxis pública ni
> contaminar el AST semántico neutral.

```text
Código Cobra
     ↓
Lexer
     ↓
Parser
     ↓
AST / IR neutral Cobra
     ↓
Análisis semántico
     ↓
 ┌───────────┬────────────┬──────────┬──────────┐
 │  Runtime  │   Python   │    JS    │   Rust   │
 └───────────┴────────────┴──────────┴──────────┘
```

Una representación propia del destino solo puede aparecer **después** de la
frontera neutral. Ningún detalle cómodo para un backend justifica contaminar el
frontend o el AST/IR neutral.

## 3. Contrato sintáctico objetivo

El **contrato normativo** implementado por el Parser es:

```cobra
clase Persona:
    metodo inicializar(este, nombre):
        atributo este nombre = nombre

    metodo saludar(este):
        imprimir "Hola " + atributo este nombre
fin
```

Este fragmento es el contrato aprobado y el Parser lo acepta desde el cierre de
POO-001 en Task 42C.

El futuro smoke E2E contractual es:

```cobra
clase Persona:
    metodo inicializar(este, nombre):
        atributo este nombre = nombre

    metodo saludar(este):
        imprimir "Hola " + atributo este nombre
fin

var persona = Persona("Adolfo")
persona.saludar()
```

Resultado observable exacto:

```text
Hola Adolfo
```

El cierre de la reconstrucción exige que el programa se acepte desde **fuente
Cobra real**, atraviese la cadena declarada y produzca ese resultado en el
runtime y en cada backend cuyo subconjunto POO se declare soportado. Una prueba
con AST construido manualmente no satisface este criterio.

# DECISIONES CERRADAS

## 4. Referencia propia: `este`

La referencia propia Cobra aprobada es `este`:

```cobra
metodo saludar(este):
atributo este nombre
atributo este nombre = nombre
```

La sintaxis pública nueva no usará `self` ni `this`. `self` solo podrá ser una
representación generada por Python y `this`, una representación generada por
JavaScript. Semánticamente, `este` representa la instancia Cobra; el runtime
Cobra debe operar sobre esa semántica y no sobre el lexema Python `self`.

### `este` y el Lexer

La evidencia actual es:

```text
self → IDENTIFICADOR
este → IDENTIFICADOR
```

**Decisión:** no introducir un token específico para `este` mientras no exista
evidencia técnica que lo haga necesario. Inicialmente será un identificador
contextual con semántica POO. Esto evita reservar globalmente una palabra y
minimiza cambios del Lexer. Una propuesta de `TipoToken.ESTE` deberá justificar
la necesidad y actualizar primero este contrato.

## 5. Constructor Cobra: `inicializar`

La declaración pública aprobada es:

```cobra
metodo inicializar(este, ...)
```

El usuario Cobra no deberá escribir `__init__`, `constructor` ni `new` para
declarar el constructor. La separación obligatoria es:

```text
Cobra:      inicializar
Python:     __init__
JavaScript: constructor
Rust:       representación idiomática definida por su backend
```

## 6. Neutralidad del AST

Defecto confirmado actual:

```text
inicializar
    ↓ Parser
__init__
    ↓
NodoMetodo.nombre
```

Esto se clasifica como **FUGA DE PYTHON AL AST COBRA**. El AST neutral debe
conservar identidad Cobra. La preferencia contractual es
`NodoMetodo.nombre == "inicializar"`, o una representación semántica neutral
equivalente, sin fijar todavía una clase AST nueva. Los backends transformarán:

```text
inicializar → __init__
inicializar → constructor
inicializar → representación Rust
```

`__init__`, `self`, `this` y `constructor` pertenecen exclusivamente a las
representaciones de destino indicadas, nunca al AST neutral objetivo.

## 7. Cierre de métodos

**REPRODUCTOR HISTÓRICO ANTERIOR A 42C:** el Parser requería:

```cobra
clase Persona:
    metodo inicializar(este, nombre):
        atributo este nombre = nombre
    fin

    metodo saludar(este):
        imprimir "Hola " + atributo este nombre
    fin
fin
```

Esta forma sirve únicamente para reproducir la implementación anterior: no es
el contrato sintáctico objetivo, el smoke futuro ni un criterio de cierre. Que
el Parser la acepte no crea un segundo dialecto oficial ni decide compatibilidad
permanente.

**CONTRATO NORMATIVO (42C / POO-001 RESUELTO): los métodos NO llevan `fin`
individual.** El Parser delimita cada cuerpo mediante el siguiente `metodo` (o
su forma de método asíncrono) o el `fin` de clase. Los bloques anidados continúan
consumiendo sus propios cierres. La forma histórica se conserva temporalmente
cuando su cierre individual es estructuralmente inequívoco, sin convertirla en
un segundo contrato normativo.

La auditoría posterior de 42C detectó que `func` y `asincronico func` locales se
interpretaban erróneamente como el siguiente método de clase. Task 42C.1 corrigió
esa regresión, pero una segunda auditoría descubrió la ambigüedad inversa: un
`func` histórico situado después de un método normativo podía quedar absorbido
por este. Task 42C.2 intentó distinguir ambos contextos mediante la columna de la
declaración; Task 42C.3 retira esa solución porque la indentación no forma parte
de la gramática Cobra y dos secuencias de tokens iguales no deben producir AST
distintos.

El Libro establece `metodo` para declarar métodos, mientras que la SPEC, la
gramática EBNF y la especificación técnica establecen `func` para funciones. Una
vez abierto el cuerpo de un método, no existe información puramente sintáctica
que distinga un `func` local de un supuesto alias histórico de método hermano:
ambos casos tienen la misma secuencia de tokens, incluso cuando la función lleva
su `fin`. Por ello se aplica el contrato normativo: dentro de un método, `func` y
`asincronico func` siempre son funciones locales, sin considerar su columna. El
siguiente método debe declararse con `metodo` (o `asincronico metodo`).

Se conserva la compatibilidad histórica inequívoca: un `func` encontrado por
`declaracion_clase()` cuando no hay un método abierto todavía se sigue
convirtiendo en `NodoMetodo`. Esta compatibilidad del Parser no se promociona a
sintaxis normativa. Las pruebas fijan tanto esa excepción histórica como la
interpretación normativa del caso ambiguo y la independencia de la indentación.
Con esta decisión tokenística, POO-001 queda definitivamente resuelto.

## 8. Atributos

La forma canónica inicial de lectura es `atributo este nombre` y la de escritura
es `atributo este nombre = nombre`. No se promociona `este.nombre` a sintaxis
normativa aunque hoy se acepte parcialmente. `este.nombre = nombre` se rechaza
actualmente y tampoco forma parte del contrato. Una sintaxis punteada requerirá
una extensión normativa independiente.

## 9. Instanciación y llamadas de método

`var persona = Persona("Adolfo")` construye una representación neutral de
instancia cuando `Persona` es una clase declarada previamente
(**POO-004 — P1 — RESUELTO**).
Task 42E.1 sitúa el reconocimiento en una fase neutral
inmediatamente posterior al parseo: el Parser conserva una llamada ordinaria
durante el análisis sintáctico y `resolver_instanciaciones` la convierte en
`NodoInstancia(nombre_clase, argumentos)` usando las declaraciones visibles,
sin convenciones de mayúsculas ni nombres especiales. Los argumentos se
conservan en su orden y las funciones continúan como `NodoLlamadaFuncion`.
La caché conserva el AST sintáctico y aplica la resolución tanto en aciertos
como en fallos, por lo que una entrada creada antes de 42E no cambia la
semántica observable. Task 42E.1.1 unifica los consumidores de producto en
una frontera pública de AST resuelto y mantiene la caché SQLite como una
optimización opcional: sin `SQLITE_DB_KEY`, la frontera usa directamente
Lexer, Parser y resolución neutral. Task 42E.1.2 completa la migración a esa
frontera de los entrypoints de producto de ejecución, verificación,
transpilación, perfilado, benchmarks y Jupyter; `compilar` y
`benchtranspilers` ya no exigen una clave SQLite para usar el fallback sin
caché. Task 42E.2 completa el contrato con un modelo de bindings visibles:
una declaración de clase habilita la conversión mientras que una asignación,
una función o un parámetro posterior con el mismo nombre la enmascara. Los
parámetros y asignaciones locales sólo alteran el ámbito de su función o
método. Task 42E.2.1 completa el merge conservador y Task 42E.2.3 alinea la
propagación de escrituras de `con` con la profundidad real de runtime. Task
42E.2.4 completa el seguimiento path-sensitive del alcance; POO-004 se
mantiene **RESUELTO** tras cubrir esos escenarios.

Los bloques de control (`si`/`sino`, `mientras` y `para`) operan sobre el ámbito
de runtime existente, pero el resolver estático no confunde recorrer una rama
con ejecutarla. Resuelve cada camino sobre una copia y hace un merge
conservador: sólo conserva un binding de clase u otro binding cuando todos los
caminos posibles coinciden; una discrepancia queda ambigua y no se convierte
posteriormente en instancia. No se añade evaluación de constantes, por lo que
incluso `si falso` contempla estáticamente ambos caminos. Los bucles fusionan
el estado de cero iteraciones con el de una iteración analizada, incluida la
variable iteradora de `para`.

El alcance de cada nombre también se modela con tres estados: global seguro,
local seguro o ambiguo según el camino. Dos caminos globales conservan el
alcance global y dos caminos locales conservan el local; cualquier mezcla de
global y local, o con un alcance ya ambiguo, produce alcance ambiguo. La
ausencia de un nombre se considera no global, de modo que una declaración
local condicional no inventa un binding global. `si`/`sino`, `mientras` y
`para` reciben explícitamente el contexto de módulo, por lo que las
declaraciones realizadas en sus bloques mantienen el alcance que usa runtime.

Los scopes reales de funciones y métodos aíslan sus bindings. El entorno hijo
de `con` aísla sus declaraciones locales (incluidos su alias y las clases). En
runtime, una asignación normal busca el entorno más cercano que contiene el
nombre: desde un `con` global actualiza el binding global; desde un `con`
dentro de función, un binding global también se actualiza, pero un binding de
la función (índice intermedio entre global y el `con`) se sombrea en el entorno
actual. Los `con` más profundos conservan esa misma regla: sólo atraviesan los
entornos intermedios para escribir en global; un nombre inexistente se crea en
el `con` actual y no escapa.

Task 42E.2.3 transporta esas escrituras globales como un efecto componible del
mismo análisis conservador de bindings. Una escritura directa se propaga; en
`si`, sólo un efecto coincidente en ambas ramas queda determinado y cualquier
diferencia queda ambigua; `mientras` y `para` fusionan el efecto de cero
iteraciones con el de la iteración analizada. Un `con` anidado entrega sus
efectos al `con` exterior, mientras las declaraciones locales y el alias no
producen efectos externos. El resolver no interpreta condiciones ni
iterables. Si el alcance del destino depende del camino, la escritura se
propaga como efecto externo ambiguo: conserva la posibilidad de modificar el
binding global sin afirmar que lo hace en todos los caminos.
La resolución memoiza cada nodo por identidad:
si varios atributos apuntan al mismo nodo, como `NodoAsignacion.expresion` y
`NodoAsignacion.valor`, ambos siguen apuntando al mismo objeto transformado.

La resolución respeta el orden del programa: no incorpora referencias hacia
delante. Si un mismo ámbito declara clase y función con el mismo nombre, la
fase neutral no inventa precedencia y conserva la llamada genérica; el análisis
semántico existente rechaza después la declaración duplicada.

Las llamadas aprobadas son `persona.saludar()` y
`persona.cambiar_nombre("Ana")`. Desde 42D ambas formas producen un único
`NodoLlamadaMetodo`, conservando el objeto, el nombre y los argumentos en orden
(**POO-005 — P1 — RESUELTO**). El encadenamiento posterior a una llamada, como
`objeto.obtener().saludar()`, queda fuera del alcance de 42D.

Task 42D.1 fija la separación inspirada en Python: `metodo` es la palabra
reservada de declaración; el nombre real del método es un `IDENTIFICADOR`, y es
ese identificador el que se usa en las llamadas postfix. Con este contrato,
POO-005 queda cerrado definitivamente.

## 10. Runtime, receptor y aridad

Hay capacidades internas construidas sobre AST manual (`NodoInstancia`,
`NodoLlamadaMetodo`, herencia, override y atributos), pero eso **no demuestra
soporte público**. Toda evaluación debe distinguir:

```text
CAPACIDAD INTERNA
CAPACIDAD ALCANZABLE DESDE FUENTE COBRA
```

Actualmente el runtime define `self`, descarta por posición el primer parámetro
y enlaza con `zip`, sin contrato neutral suficiente. El objetivo es que `este`
represente la instancia Cobra y que cada llamada/constructor valide de forma
determinista receptor, argumentos faltantes y argumentos sobrantes. No se
conservará un `zip(...)` que descarte argumentos silenciosamente.

## 11. Contratos de backend

### Python

```text
inicializar → __init__
este        → self
clase vacía → pass
instancia   → Clase(...)
método      → objeto.metodo(...)
```

Estas transformaciones pertenecen exclusivamente al backend Python.

### JavaScript

```text
inicializar → constructor
este        → this
instancia   → new Clase(...)
método      → objeto.metodo(...)
```

No son resultados finales aceptables `__init__(este, ...)` ni `Persona(...)`
cuando semánticamente se construye un objeto.

### Rust

Rust no traducirá literalmente el modelo Python. Su tarea definirá el
subconjunto soportado y una representación idiomática basada, cuando proceda,
en `struct`, `impl`, `new`, campos y receptor. Toda capacidad no soportada debe
producir un diagnóstico explícito, no código aparentemente válido pero erróneo.

## 12. Herencia, override y `super`

Estado actual:

```text
simple    → parcial
múltiple  → divergente
override  → parcial/manual
super     → no soportado
```

Orden obligatorio de trabajo:

```text
instancia
→ llamada método
→ constructor/binding
→ atributos
→ backends básicos
→ herencia/override
```

No se reparará herencia antes de que la POO elemental sea alcanzable desde
fuente. `super`, `superclase`, `padre` y `base` no tienen contrato público
aprobado como operación equivalente a `super`. No se inventará esa sintaxis
durante esta secuencia; cualquier soporte futuro exige decisión normativa
independiente.

## 13. Decisiones pendientes (no improvisar)

1. Mecanismo exacto de delimitación de métodos sin `fin` por método.
2. Representación neutral concreta del constructor/receptor si conservar el
   nombre no basta; no se presupone una clase AST nueva.
3. Fase responsable de resolver `Persona(...)` como instancia.
4. Contrato para miembros de clase distintos de métodos: rechazo explícito o
   modelo neutral.
5. Subconjunto POO y representación idiomática de Rust.
6. Alcance compatible de herencia múltiple por backend.
7. Posible sintaxis punteada, pospuesta como extensión independiente.
8. Operación equivalente a `super`, fuera de esta reconstrucción.

## 14. Hallazgos POO permanentes

Estados permitidos: `PENDIENTE`, `EN PROGRESO`, `RESUELTO`,
`NO SOPORTADO POR CONTRATO`, `POSPUESTO EXPLÍCITAMENTE`. Nada se marca resuelto
sin prueba. Task 42A no resuelve ninguna reparación productiva.

| ID | Severidad | Problema | Estado | Tarea |
|---|---|---|---|---|
| POO-001 | P1 | métodos delimitados por el siguiente `metodo` o el `fin` de clase, sin `fin` individual | RESUELTO | 42C |
| POO-002 | P1 | `inicializar → __init__` ocurre en frontend/AST | PENDIENTE | 42C |
| POO-003 | P1 | binding neutral de `este` ausente | PENDIENTE | 42C/42G |
| POO-004 | P1 | instanciación inalcanzable desde fuente | RESUELTO | 42E |
| POO-005 | P1 | llamada de método postfix inalcanzable/corrupta | RESUELTO | 42D |
| POO-006 | P1 | constructor no se ejecuta en runtime | PENDIENTE | 42G |
| POO-007 | P2 | aridad y receptor runtime no se validan | PENDIENTE | 42G |
| POO-008 | P2 | backend Python genera clase vacía inválida | PENDIENTE | 42H |
| POO-009 | P2 | JS no adapta constructor/receptor/instancia | PENDIENTE | 42I |
| POO-010 | P2 | representación POO Rust incompleta | PENDIENTE | 42J |
| POO-011 | P2 | herencia divergente y E2E bloqueado | PENDIENTE | 42K |
| POO-012 | P2 | atributo de clase en contenedor incorrecto | PENDIENTE | 42F |
| POO-013 | P2 | identidad AST depende de namespace/orden de importación | RESUELTO | 42B |
| POO-014 | P3 | documentación y ejemplos contradicen frontend/objetivo | PENDIENTE | 42M |
| POO-015 | P3 | operación `super` sin contrato aprobado | NO SOPORTADO POR CONTRATO | decisión futura independiente |
| POO-016 | P2 | semántico rechaza `NodoAtributo` como destino | PENDIENTE | 42F |

### POO-013 — reproducción y causa demostrada

Con `PYTHONPATH=src:src/pcobra`, la importación normal directa de
`core.ast_nodes` y `pcobra.core.ast_nodes` puede terminar exponiendo la misma
clase (`NodoAST_A is NodoAST_B` es `True` y ambos `isinstance` son `True`). Sin
embargo, si se importa primero un transpilador mediante el namespace legado
`cobra...`, `constant_folder` captura durante su carga otra identidad de
`pcobra.core.ast_nodes.NodoAST`. Después, aunque los módulos visibles queden
aliasados, el optimizador conserva esa referencia obsoleta:

```text
NodoAST de core.ast_nodes is NodoAST visible de pcobra.core.ast_nodes → True
NodoAST de core.ast_nodes is NodoAST capturado por constant_folder    → False
isinstance(nodo legado, NodoAST visible)                              → True
isinstance(nodo legado, NodoAST de constant_folder)                   → False
RuntimeError: Estructura AST inválida en optimización (constant_folder) en 'NodoInstancia': NodoInstancia
```

El mismo patrón afecta `NodoLlamadaMetodo`. En orden `core` o `pcobra.core`
primero, todas las identidades coinciden y los nodos atraviesan
`constant_folder`; las instancias canónicas también lo atraviesan cuando no se
ha capturado la identidad divergente. Por tanto, la causa final es
**incompatibilidad de identidad AST entre namespaces dependiente del orden de
importación**, no falta de casos/passthrough POO en `constant_folder`. No debe
“repararse” añadiendo casos artificiales al optimizador; 42B normalizará la
identidad/compatibilidad de namespaces antes de que contamine pruebas 42C–42J.

**Resolución Task 42B.** `pcobra.core.ast_nodes` registra tempranamente
`core.ast_nodes` (y viceversa) como nombre alternativo del mismo objeto módulo.
Las pruebas en intérpretes limpios cubren ambos órdenes con la ruta histórica
primero en `PYTHONPATH`, verifican la identidad de las clases POO, el
`isinstance` cruzado y el paso de un `NodoInstancia` legado por
`constant_folder`. La corrección actúa sobre la carga del módulo y no añade
passthroughs al optimizador.

**Estabilización Task 42B.1.** El registro del nombre alternativo consulta la
política existente mediante `_resolve_legacy_import_policy`: solo crea el alias
cuando la fase y el opt-in vigentes permiten imports legacy. Además,
`pcobra.core` enlaza explícitamente su atributo `ast_nodes` con el módulo
canónico, incluso si un import legacy previo ya había precargado ese objeto en
`sys.modules`. Las sondas en procesos limpios demuestran ambos órdenes con
legacy permitido, el acceso por `pcobra.core.ast_nodes`, la identidad única y
el caso funcional de `constant_folder`; otra sonda en fase 2 sin opt-in
demuestra que importar el AST canónico no registra `core.ast_nodes`. Sin
embargo, la auditoría posterior detectó que la ruta física histórica aún
permitía cargar
`core.ast_nodes` como una segunda copia cuando legacy estaba deshabilitado, por
lo que este cierre fue prematuro.

**Estabilización Task 42B.2.** La carga directa de `core.ast_nodes` consulta la misma
política y ahora se rechaza explícitamente cuando legacy está deshabilitado. Las
pruebas en procesos limpios cubren fase 2 con y sin opt-in, fase 3 incluso con
opt-in, ambos órdenes autorizados, identidad de módulo y clases, y el caso
funcional cruzado de `constant_folder`. La auditoría posterior encontró aún un
bypass en un checkout normal: con `cwd` en la raíz y `PYTHONPATH=src`, el shim
físico `core/__init__.py` importaba primero `pcobra.core` y copiaba todos sus
submódulos cargados a claves `core.*`. Así introducía `core.ast_nodes` en
`sys.modules` antes de que pudiera ejecutarse el rechazo de 42B.2.

**Cierre Task 42B.3.** El shim de checkout consulta ahora
`pcobra._resolve_legacy_import_policy()` antes de importar el paquete canónico o
copiar submódulos. Si legacy está deshabilitado, rechaza la carga sin registrar
ningún alias `core.*`; si está permitido, conserva el mecanismo común y la
identidad única de módulo y clases. Las sondas en procesos Python limpios desde
la raíz, con `PYTHONPATH=src`, prueban fase 1, fase 2 con y sin opt-in, y fase 3
con y sin opt-in. También comprueban que el import canónico funciona en todos
los casos y que `constant_folder` opera con los nodos canónicos. Una auditoría
posterior descubrió un segundo shim en `src/core/__init__.py`, accesible desde un
directorio externo con `PYTHONPATH=ROOT/src`, que todavía omitía la política; por
tanto, este cierre también fue prematuro.

**Cierre Task 42B.4.** El segundo shim consulta ahora la misma función canónica
`pcobra._resolve_legacy_import_policy()` antes de importar `pcobra.core`, emitir
su aviso o registrar aliases. Una sonda específica ejecutada desde un directorio
temporal con únicamente `ROOT/src` en `PYTHONPATH` verifica expresamente que
`core.__file__` corresponde a `ROOT/src/core/__init__.py`, cubre las fases 1, 2
y 3 con las variantes de opt-in pertinentes, y confirma identidad AST,
ausencia de aliases cuando legacy está prohibido, funcionamiento canónico y
`constant_folder`. Tras probar tanto el shim raíz como este segundo shim en las
tres fases, POO-013 vuelve a considerarse resuelto.

### POO-016 — reproducción y contrato de reparación

Con los cierres que hoy requiere el Parser:

```cobra
clase C:
    metodo f(este):
        atributo este nombre = nombre
    fin
fin
```

el Parser produce `NodoAsignacion` cuyo destino es `NodoAtributo`. El analizador
semántico recorre `visit_asignacion`, pasa ese nodo a `_validar_nombre` como si
fuera un nombre simple y obtiene exactamente:

```text
TypeError: El nombre debe ser string, no <class 'pcobra.core.ast_nodes.NodoAtributo'>
```

La reparación debe aceptar o validar semánticamente `NodoAtributo` como destino
según el contrato POO sin debilitar asignaciones ordinarias. Es dependencia de
42F y debe estar corregido antes del smoke E2E; 42A solo lo documenta.

## 15. Secuencia de microtareas

La reproducción de POO-013 demuestra que puede contaminar pruebas posteriores,
por lo que recibe una microtarea temprana y el resto se renumera:

1. **42A — auditoría + roadmap.** Reproducciones y trazabilidad; ningún
   cambio productivo.
2. **42A.1 — alineación normativa Libro ↔ Roadmap.** Resuelve la gobernanza y la
   divergencia histórica documental; no repara POO productiva.
3. **42A.2 — alineación documental con la gramática vigente.** Documentar el
   `fin` actualmente requerido por método y una única expresión en `imprimir`,
   sin alterar las decisiones POO ni reparar código productivo.
4. **42B — compatibilidad de identidad AST.** Normalizar `core.ast_nodes`,
   `pcobra.core.ast_nodes` y rutas relacionadas, con ambos órdenes de import.
5. **42C — cierre de métodos (POO-001).** Hacer parseable el contrato aprobado
   sin `fin` individual; no incluye la neutralidad pendiente de constructor o
   receptor (POO-002/POO-003).
6. **42D — llamada de método postfix desde texto.** Un nodo completo para 0/N
   argumentos, sin tokens residuales ni aceptación fragmentada.
7. **42E — resolución neutral de instanciación.** Distinguir clase y función en
   la fase neutral que se decida explícitamente.
8. **42F — atributos + analizador semántico + cuerpo de clase.** Incluye
   POO-016, lectura/escritura canónica y POO-012.
9. **42G — runtime: constructor, `este`, aridad y llamadas.** Smoke desde fuente,
   no AST manual.
10. **42H — backend Python.** `__init__`, `self`, `pass`, instancia y método solo
   tras la frontera neutral.
11. **42I — backend JavaScript.** `constructor`, `this`, `new` y llamada.
12. **42J — backend Rust.** Subconjunto explícito, representación idiomática y
    diagnóstico para lo no soportado.
13. **42K — herencia y override.** Después de POO elemental; `super` permanece
    fuera del contrato.
14. **42L — E2E contractual.** El programa de §3 produce exactamente
    `Hola Adolfo` en los destinos declarados.
15. **42M — documentación, SPEC, Libro y ejemplos.** Solo describe lo realmente
    implementado y probado.

Cada tarea debe reproducir primero su defecto, autorizar expresamente cualquier
capa sensible, añadir prueba focal y comparar nuevos fallos contra su SHA base.
No se inicia automáticamente una tarea posterior.

## 16. Criterios de cierre de la reconstrucción

La reconstrucción POO solo termina cuando hay evidencia focal y E2E de que:

- el fragmento contractual se parsea sin cierres de método añadidos;
- AST/IR conserva `inicializar` y semántica neutral de `este`;
- instancia, llamadas y atributos nacen de fuente Cobra y forman nodos/IR
  completos;
- semántico acepta destinos atributo válidos sin relajar nombres ordinarios;
- runtime ejecuta constructor y métodos con receptor/aridad deterministas;
- Python y JS generan y ejecutan sus representaciones propias;
- Rust compila su subconjunto declarado o diagnostica explícitamente lo demás;
- herencia/override solo se declaran soportados donde haya E2E;
- el smoke imprime exactamente `Hola Adolfo`;
- POO-001…POO-014 y POO-016 solo pasan a `RESUELTO` con pruebas, y POO-015
  conserva su estado hasta una decisión normativa separada;
- finalmente SPEC, Libro y ejemplos reflejan comportamiento real probado.

## 17. Documentación

> El Libro puede fijar decisiones normativas antes de que termine su
> implementación, siempre que distinga visiblemente contrato y estado. SPEC,
> ejemplos ejecutables y advertencias transitorias se reconciliarán por completo
> al final de la reconstrucción.

No se modificará documentación para aparentar que una característica funciona.
Task 42M sigue siendo necesaria para retirar advertencias transitorias,
actualizar ejemplos ejecutables, limpiar compatibilidad documental histórica,
documentar exactamente lo probado y cerrar POO-014.

# INVARIANTES — NO ROMPER

1. La sintaxis pública POO es española.
2. `este` es la referencia propia aprobada.
3. `inicializar` es el constructor aprobado.
4. `self` no es sintaxis pública nueva.
5. `__init__` no pertenece al AST neutral objetivo.
6. `this` no pertenece al AST neutral.
7. `constructor` no pertenece al AST neutral.
8. Python/JS/Rust no dictan la sintaxis Cobra.
9. No añadir tokens al Lexer sin evidencia.
10. No considerar AST manual como E2E.
11. No declarar una capacidad completa sin fuente Cobra.
12. No ocultar fallos mediante `skip`/`xfail`.
13. No debilitar assertions para conseguir verde.
14. No modificar Parser fuera de una microtarea autorizada.
15. No introducir compatibilidad accidental como sintaxis normativa.
16. No inventar `super` durante esta secuencia.
17. No actualizar SPEC/Libro como si el roadmap ya estuviera implementado.
18. Cada tarea debe reproducir el defecto antes de modificarlo.
19. Cada reparación debe tener prueba focal.
20. Cada fallo nuevo debe compararse contra el SHA base.

## 18. Cabecera obligatoria para futuras tareas POO

Copiar esta plantilla en futuros prompts:

```text
ANTES DE MODIFICAR POO:

1. Leer docs/POO_ROADMAP.md.
2. Confirmar SHA base.
3. Identificar POO-xxx afectado.
4. Reproducir el defecto.
5. Respetar las decisiones cerradas.
6. No ampliar alcance.
7. Ejecutar pruebas focales.
8. Comparar fallos contra base.
9. Actualizar el estado del roadmap solo con evidencia.
```
