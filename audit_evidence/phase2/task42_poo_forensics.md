# Task 42 — Auditoría forense integral de POO y contrato sintáctico español

**Estado:** `Task 42 — AUDITORÍA COMPLETA`
**No significa:** `POO — RESUELTA`
**SHA auditado:** `f12648682b9a019a10aa3d84e6b285c7d17ca73c` (`HEAD` al iniciar; rama `work`).
**Fecha:** 2026-09-20.
**Alcance:** exclusivamente observación. No se modificaron Lexer, Parser, AST, runtime, backends, pruebas ni documentación normativa.

> **Actualización Task 42A:** `docs/POO_ROADMAP.md` es la fuente contractual permanente posterior a esta auditoría histórica. Esta actualización añade POO-016, corrige la causa de POO-013 tras reproducirla y ajusta dependencias; no afirma que la POO esté reparada.

## 1. Metodología y contrato objetivo

Se leyó la cadena pública y sus adaptadores (`src/pcobra/cobra/core/*` reexporta en varios casos la implementación de `src/pcobra/core/*`), los tres backends oficiales, el analizador semántico, documentación, ejemplos y pruebas. Se ejecutaron reproductores con `PYTHONPATH=src`, siempre a partir de texto real, y se distinguieron de pruebas que construyen el AST a mano. Los fragmentos temporales se guardaron fuera del repositorio (`/tmp/task42_probe.py`).

Contrato futuro impuesto por Task 42 (no implementado):

```cobra
clase Persona:
    metodo inicializar(este, nombre):
        atributo este nombre = nombre

    metodo saludar(este):
        imprimir "Hola", atributo este nombre
fin
```

Separación requerida: sintaxis Cobra (`inicializar`, `este`) → semántica/AST neutral → representación del backend (`__init__/self`, `constructor/this`, `new/&self`, según corresponda). El estado actual incumple esa separación.

## 2. Inventario Lexer

La precedencia de patrones produce tokens específicos para las palabras POO declaradas antes de `IDENTIFICADOR`; no existe un registro separado que convierta `self`, `este`, `super` o `inicializar`.

| Palabra | Token actual | Reservada (`PALABRAS_RESERVADAS`) | Canónica/documentada hoy | Alias | Identificador ordinario |
|---|---|---:|---|---|---:|
| `clase` | `CLASE` | sí | sí | no | no |
| `estructura` | `ESTRUCTURA` | sí | documentada como alias de clase | sí, de `clase` | no |
| `registro` | `REGISTRO` | sí | documentada como alias de clase | sí, de `clase` | no |
| `metodo` | `METODO` | sí | sí | no | no |
| `atributo` | `ATRIBUTO` | sí | sí | no | no |
| `inicializar` | `IDENTIFICADOR` | no | alias especial documentado | sí, semántico a `__init__` | sí |
| `self` | `IDENTIFICADOR` | no | usado por SPEC, Libro, ejemplos y tests | no | sí |
| `este` | `IDENTIFICADOR` | no | objetivo nuevo; ausente del contrato vigente | no | sí |
| `super` | `IDENTIFICADOR` | no | no como sintaxis POO Cobra | no | sí |
| `interface` | `INTERFACE` | sí | alias documentado | sí, de `rasgo` | no |
| `rasgo` | `INTERFACE` | sí | forma española documentada | comparte token | no |
| `enumeracion` / `enum` | `ENUMERACION` | sí | relacionada con tipos, no clases | `enum` es alias | no |

Conclusión `self/este`: ambos viajan hoy exactamente como `IDENTIFICADOR`; el Lexer no les atribuye semántica. Técnicamente `este` no necesita necesariamente token propio: el Parser/runtime/backends pueden imponer el significado contextual conservándolo como identificador. La elección entre identificador contextual y token se deja a 42A; no hay evidencia que obligue a ampliar el Lexer.

## 3. Inventario Parser y texto realmente aceptado

- `declaracion_clase` acepta `clase|estructura|registro Nombre`, genéricos opcionales, cero o más bases entre paréntesis, `:`, cualquier declaración hasta `fin`. Cada método exige además su propio `fin`.
- `declaracion_metodo` acepta `metodo` o `func`, nombre identificador, parámetros identificadores, `:`, cuerpo y `fin`. Convierte el nombre mediante `ALIAS_METODOS_ESPECIALES` **antes** de construir `NodoMetodo`, aunque conserva `nombre_original`.
- `exp_atributo` acepta `atributo objeto nombre` y crea `NodoAtributo`. `termino` acepta también cadenas `objeto.nombre` como `NodoAtributo`.
- `declaracion_asignacion` reconoce como destino `atributo objeto nombre`; no reconoce `objeto.nombre = valor`.
- `llamada_funcion` solo reconoce `IDENTIFICADOR(...)` y crea `NodoLlamadaFuncion`, sin resolución contextual de clase a `NodoInstancia`.
- `termino` consume `objeto.atributo`, pero nunca el sufijo de llamada. `persona.saludar()` no crea `NodoLlamadaMetodo`.
- `expresion` no repara estas omisiones: es la entrada de precedencia que termina en `termino`.
- `imprimir` consume una sola expresión. La forma objetivo `imprimir "Hola", ...` deja la coma fuera; no ofrece impresión variádica en esta producción.

### Formas observadas

| Construcción textual | Resultado actual | Clasificación contractual |
|---|---|---|
| clase con `fin` por método y por clase | `NodoClase`/`NodoMetodo` | ACEPTADA |
| clase objetivo con un único `fin` final | el segundo `metodo` se intenta analizar dentro del primero; `ParserError` | RECHAZADA |
| `metodo f(self)` | parámetro `"self"` | ACEPTADA, fuga pública actual |
| `metodo f(este)` | parámetro `"este"` | ACEPTADA como identificador ordinario |
| `atributo este nombre` | `NodoAtributo(NodoIdentificador("este"), "nombre")` | ACEPTADA |
| `atributo este nombre = nombre` | `NodoAsignacion(variable=NodoAtributo(...), ...)` | ACEPTADA |
| `este.nombre` | `NodoAtributo(...)` | ACEPTADA ACCIDENTALMENTE; no promover a contrato |
| `este.nombre = nombre` | `ParserError: Token inesperado en término: TipoToken.ASIGNAR` | RECHAZADA |
| `Persona("Adolfo")` | `NodoLlamadaFuncion("Persona", ...)` | ACEPTADA, nodo incorrecto para runtime POO |
| `persona.saludar()` | atributo seguido de `(`; con cero args termina en `ParserError: Token inesperado en término: TipoToken.RPAREN` | RECHAZADA |
| `persona.cambiar_nombre("Ana")` | dos nodos espurios: `NodoAtributo` y `NodoValor("Ana")`; no error | ACEPTACIÓN ACCIDENTAL |
| `clase C(A, B): fin` | `NodoClase.bases == ["A", "B"]` | ACEPTADA sintácticamente |
| `clase C: var x = 1 fin` | `NodoAsignacion` guardado en `metodos` | ACEPTACIÓN ACCIDENTAL — NO CONTRATO |

## 4. Constructor y `ALIAS_METODOS_ESPECIALES`

`ALIAS_METODOS_ESPECIALES`, en `src/pcobra/cobra/core/utils.py`, se aplica tanto a funciones como a métodos en el Parser. Tabla completa:

| Cobra | AST actual | Python actual | JavaScript actual | Rust actual |
|---|---|---|---|---|
| `asignar_atributo` | `__setattr__` | `def __setattr__` | `__setattr__(...)` | `fn __setattr__` |
| `borrar_atributo` | `__delattr__` | dunder | dunder literal | dunder literal |
| `borrar_item` | `__delitem__` | dunder | dunder literal | dunder literal |
| `booleano` | `__bool__` | dunder | dunder literal | dunder literal |
| `comparar` | `__eq__` | dunder | dunder literal | dunder literal |
| `contener` | `__contains__` | dunder | dunder literal | dunder literal |
| `entrar` | `__enter__` | dunder | dunder literal | dunder literal |
| `entrar_async` | `__aenter__` | dunder | dunder literal | dunder literal |
| `inicializar` | `__init__` | `def __init__` | `__init__(...)`, no `constructor` | `fn __init__`, no `new` |
| `iterar` | `__iter__` | dunder | dunder literal | dunder literal |
| `llamar` | `__call__` | dunder | dunder literal | dunder literal |
| `longitud` | `__len__` | dunder | dunder literal | dunder literal |
| `obtener_atributo` | `__getattr__` | dunder | dunder literal | dunder literal |
| `obtener_hash` | `__hash__` | dunder | dunder literal | dunder literal |
| `obtener_item` | `__getitem__` | dunder | dunder literal | dunder literal |
| `ordenar` | `__lt__` | dunder | dunder literal | dunder literal |
| `poner_item` | `__setitem__` | dunder | dunder literal | dunder literal |
| `representar` | `__repr__` | dunder | dunder literal | dunder literal |
| `salir` | `__exit__` | dunder | dunder literal | dunder literal |
| `salir_async` | `__aexit__` | dunder | dunder literal | dunder literal |
| `texto` | `__str__` | dunder | dunder literal | dunder literal |

La tarea menciona `cadena` e `igual`, pero no existen; sus equivalentes actuales son `texto` y `comparar`. Estos nombres españoles podrían ser abstracciones Cobra legítimas, pero su representación AST es enteramente Python. Clasificación: **FUGA DE PYTHON AL AST COBRA**, no normalización neutral. `nombre_original` reduce pérdida diagnóstica, pero todos los consumidores reciben el dunder y JS/Rust lo emiten literalmente.

Las tres formas `inicializar(este, ...)`, `inicializar(self, ...)` y `__init__(self, ...)` tokenizan y parsean si se añaden los cierres exigidos. Las dos primeras terminan en `NodoMetodo(nombre="__init__", nombre_original="inicializar")`; la tercera conserva ambos campos como `__init__`.

## 5. AST: alcance real

| Nodo | Parser desde texto | Runtime | Python | JS | Rust | Evidencia predominante |
|---|---:|---:|---:|---:|---:|---|
| `NodoClase` | sí | sí | sí | sí | sí | fuente y AST manual |
| `NodoMetodo` | sí | sí, dentro de clase | sí | sí | sí | fuente y AST manual |
| `NodoAtributo` | sí (`atributo`, también punto) | sí | sí | sí | valor sí; visita como sentencia incompleta | fuente y AST manual |
| `NodoInstancia` | **no** | sí | visitor/valor sí | visitor/valor sí | valor sí | solo AST manual |
| `NodoLlamadaMetodo` | **no** | sí | visitor sí | visitor sí | sin visitor equivalente localizado | solo AST manual |
| `NodoAsignacion` como miembro de clase | sí accidentalmente | rompe construcción de clase | Python lo imprime; JS/Rust inválidos | idem | idem | fuente accidental |

La existencia de visitor no equivale a alcanzabilidad. Además, los tests manuales directos de `NodoInstancia` y `NodoLlamadaMetodo` fallan hoy antes del visitor Python/JS en `constant_folder`, que rechaza esos nodos.

## 6. Semántico

`visit_clase` declara la clase, exige que cada base ya sea un símbolo `clase`, detecta ciclos mediante el grafo `herencia`, abre ámbito y llama `aceptar` para cada elemento de `nodo.metodos`. `visit_metodo` declara el nombre y procesa parámetros/cuerpo. No define significado contextual para `self` ni `este`, no convierte llamadas de función en instancias y no suministra dispatch POO. Además, una escritura `atributo este nombre = nombre` produce un `NodoAsignacion` con destino `NodoAtributo`, pero `visit_asignacion` entrega ese nodo a `_validar_nombre` como si fuera un nombre simple y falla con `TypeError: El nombre debe ser string, no <class 'pcobra.core.ast_nodes.NodoAtributo'>` (POO-016). Un atributo de clase accidental llega como `NodoAsignacion` al ámbito de clase; no existe modelo explícito de campos de clase.

## 7. Runtime

- `_construir_clase` convierte **cada** elemento de `nodo.metodos` mediante `_construir_funcion`; por eso el atributo de clase accidental falla con `AttributeError: 'NodoAsignacion' object has no attribute 'parametros'`.
- `ejecutar_instancia` solo crea `{__clase__, __bases__, __atributos__}`. **No busca ni ejecuta `__init__`/`inicializar` y descarta de hecho los argumentos.**
- La fuente `Persona("Adolfo")` crea `NodoLlamadaFuncion`, no `NodoInstancia`; la ruta pública tampoco llega a `ejecutar_instancia` de forma correcta.
- `ejecutar_llamada_metodo` sí busca primero en la clase concreta y luego recursivamente en bases, lo cual implementa precedencia de override y búsqueda múltiple por orden, pero solo es accesible con AST manual.
- La instancia se liga definiendo siempre la variable runtime `self`, independientemente del nombre declarado; después elimina por **posición** el primer parámetro (`parametros[1:]`). No valida que sea `self`, ni define `este`. Con `metodo f(este)`, expresiones que referencien `este` fallarían; expresiones `self` funcionarían aunque la firma diga `este`.
- No verifica aridad de método: `zip` trunca argumentos sobrantes y deja faltantes sin binding. Las funciones ordinarias sí comparan longitudes.
- Lectura/escritura de `NodoAtributo` opera sobre `__atributos__`; lookup de método es separado. Los retornos se propagan mediante `_ControlRetorno`.
- El constructor nunca llega a ejecutarse, ni siquiera al construir manualmente `NodoInstancia`.

Herencia/override runtime existen a nivel de nodos manuales. Desde fuente se pueden registrar bases, pero no instanciar/invocar por la ruta POO, de modo que herencia y override E2E están **BLOQUEADOS POR INSTANCIACIÓN/LLAMADA DE MÉTODO**.

## 8. Backend Python

Actual: clase → `class Nombre(Bases):`; método conserva nombre/parámetros AST; atributo → punto; llamada/instancia tienen visitors. `inicializar` funciona en Python solo porque el Parser ya entregó `__init__`; `este` se emite literalmente, no se traduce a `self`. La clase vacía genera exactamente `class Vacia:\n` sin `pass`: Python inválido. Una clase con métodos vacíos sí obtiene `pass` dentro de `with ExitStack`.

La instanciación escrita como `Persona(...)` transpila por la ruta genérica de llamada, coincidentemente con sintaxis Python, pero la clase vacía hace inválido el módulo. La llamada de método no es alcanzable. El objetivo futuro debe mapear en backend, no Parser: `inicializar → __init__`, receptor `este → self`, y añadir cuerpo válido a clases vacías.

## 9. Backend JavaScript

Actual: primera base → `extends`; bases adicionales quedan en comentario. El constructor objetivo sale como `__init__(este/nombre...)`, nunca `constructor`; parámetros `self`/`este` se conservan y accesos también, nunca `this`. `Persona(...)` proveniente de `NodoLlamadaFuncion` se emite **sin `new`**; solo el inalcanzable `NodoInstancia` usaría `new`. Clases vacías sí son sintácticamente válidas. Atributos de clase accidentales generan `let x = 1;` dentro de `class`, inválido. Herencia múltiple se degrada silenciosamente a una base.

## 10. Backend Rust

Actual: clase → `struct Nombre {}` más `impl Nombre`; las bases solo aparecen como comentario, sin herencia/traits/composición. Métodos se emiten como `fn nombre(parametros)` sin tipos; `este`/`self` se copian sin construir receptores Rust válidos y `__init__` no se convierte en `new`. `NodoInstancia` como valor produciría `Clase::new(...)`, pero no existe `new`; la fuente produce `NodoLlamadaFuncion` y termina como `Clase(...)`. No se localizó visitor Rust para `NodoLlamadaMetodo`; `NodoAtributo` como sentencia produjo `NotImplementedError`. Clase vacía aislada genera estructura/impl sintácticamente plausibles, pero la POO con métodos/campos es incompleta o inválida.

## 11. Clases vacías, herencia, override, super y atributos de clase

- **Clase vacía:** Lexer/Parser/AST/runtime completos; Python roto por falta de `pass`; JS válida; Rust estructura/impl vacíos. Estado global: **ROTO**.
- **Herencia simple:** Parser llena `bases`, semántico valida orden/ciclos, runtime registra y lookup manual funciona, Python/JS representan una base, Rust solo comenta. Sin llamada desde fuente. Estado: **PARCIAL**.
- **Herencia múltiple:** Parser, semántico y runtime manual conservan todas las bases; Python las emite todas (pero clases vacías invalidan el resultado), JS usa solo la primera, Rust ninguna. Estado: **PARCIAL**.
- **Override:** el runtime busca derivada antes que bases; Python/JS lo expresarían, Rust no. Sin `NodoLlamadaMetodo` desde texto: **BLOQUEADO POR LLAMADA DE MÉTODO**, estado **PARCIAL**.
- **Superclase:** no hay token, producción, nodo ni operación pública para `super`, `superclase`, `padre` o `base`; coincidencias `padre/base` internas son ámbitos/variables host. Estado: **NO SOPORTADO**.
- **Atributo de clase:** aceptación accidental descrita arriba: runtime falla, Python casualmente válido si la clase no queda vacía, JS/Rust inválidos. Estado: **ACEPTACIÓN ACCIDENTAL**.

## 12. Fugas de lenguajes destino

| Aparición relevante | Clasificación |
|---|---|
| `self` en clases Python que implementan el compilador | IMPLEMENTACIÓN INTERNA HOST; no es hallazgo |
| `__init__`, etc. en visitors Python | DESTINO PYTHON legítimo |
| `constructor`, `this`, `extends` en generadores JS | DESTINO JAVASCRIPT legítimo cuando queda encapsulado |
| `self`, `__init__` en SPEC, Libro, ejemplos `.cobra` y tests fuente | SINTAXIS/TEST/DOCUMENTACIÓN COBRA + FUGA DE ABSTRACCIÓN |
| dunders almacenados en `NodoMetodo.nombre` por Parser | AST neutral + FUGA DE ABSTRACCIÓN |
| dunders emitidos literalmente por JS/Rust | FUGA DE ABSTRACCIÓN causada aguas arriba |
| `super` en código host (`super().__init__`) | IMPLEMENTACIÓN INTERNA HOST |

No hay soporte Cobra de `super`: buscar el lexema en capas POO no encontró una ruta pública; sus apariciones relevantes restantes son Python host o vocabulario prose.

## 13. Documentación normativa y ejemplos

- `docs/SPEC_COBRA.md` declara clase con un único cierre genérico, pero su ejemplo usa `metodo __init__(self, nombre)`, `atributo self nombre` y `imprimir "Hola", ...`; contradice el contrato español objetivo y, en cierres/impresión, el Parser real.
- `docs/LIBRO_PROGRAMACION_COBRA.md` (fuente normativa vigente) muestra `metodo __init__(nombre)` y `self.nombre = nombre`, forma que el Parser no acepta para escritura de atributo. También muestra una declaración `atributo saldo` que `exp_atributo` no acepta (requiere objeto y nombre).
- `examples/clase_metodo_atributo.cobra` y `examples/avanzados/clases/*.cobra` usan `self` y/o `__init__`. Los ejemplos sí añaden `fin` por método, exponiendo la divergencia de cierre con el nuevo contrato objetivo.
- README solo enumera tokens POO; no define una cadena E2E fiable.

No se modificó documentación: estas contradicciones quedan como evidencia, no se ocultaron.

## 14. Inventario de pruebas

| Capacidad | Test desde fuente Cobra | AST manual | Estado de cobertura |
|---|---|---|---|
| clase/método | `test_metodo_atributo.py`, `test_parser_clase.py` | también varios | cubierta desde fuente |
| `self`, alias especiales | `test_metodo_atributo.py` | no necesario | cubierta desde fuente, contrato antiguo |
| `este` receptor | no localizado | no | SIN TEST |
| atributo lectura/escritura | parser desde fuente aislada | `test_interpreter_objects.py`, `test_interpreter_atributo.py` | runtime solo AST manual |
| instancia | no: parser nunca crea nodo | `test_interpreter_objects.py`, `test_to_*_objects.py` | AST MANUAL |
| llamada método | no | mismos tests | AST MANUAL |
| constructor | alias desde fuente, ejecución no | no prueba ejecución real | parcial |
| herencia/override | parseo de bases en parser | `test_interpreter_herencia.py`, `test_interpreter_inheritance.py` | runtime AST MANUAL |
| herencia múltiple E2E | ejemplos sin smoke POO demostrativo | pruebas principalmente estructurales | insuficiente |
| clase vacía backend | no prueba validez Python | no relevante | SIN TEST E2E |
| superclase | no | no | SIN TEST / NO SOPORTADO |

Baseline POO dirigido (nueve archivos): **40 passed, 5 failed**. Fallan una expectativa runtime de atributo (`"Ana"` frente a `Ana`) y los cuatro tests manuales Python/JS de instancia/llamada porque `constant_folder` rechaza `NodoInstancia`/`NodoLlamadaMetodo`. Ejecución ampliada añadiendo `tests/unit/test_to_rust.py`: **40 passed, 25 failed**; 20 fallos Rust incluyen deuda general no exclusivamente POO, por lo que no se atribuyen todos a Task 42.

## 15. Reproductores verificables

Comando usado: `PYTHONPATH=src python /tmp/task42_probe.py` (script temporal; imprimió tokens, AST simplificado, runtime y los tres backends). Resultados esenciales:

1. Programa objetivo exacto: Lexer completa todos los tokens, incluido `este` como identificador. Parser falla en el segundo `METODO` con `ParserError: Token inesperado en término: TipoToken.METODO`; no hay AST/runtime/backends.
2. Añadiendo `fin` a cada método: `este` permanece como parámetro e identificador; no recibe binding runtime ni traducción de backend.
3. `atributo este nombre = nombre`: AST exacto conceptual `NodoAsignacion(NodoAtributo(NodoIdentificador("este"), "nombre"), NodoIdentificador("nombre"))`.
4. `var persona = Persona("Adolfo")`: `NodoAsignacion(..., NodoLlamadaFuncion("Persona", [NodoValor("Adolfo")]))`, nunca `NodoInstancia`.
5. `persona.saludar()`: error indicado; `persona.cambiar_nombre("Ana")`: `NodoAtributo` seguido de `NodoValor`, aceptación silenciosa corrupta.
6. `clase Vacia: fin`: Python `class Vacia:` sin cuerpo; JS `class Vacia {}`; Rust `struct Vacia {}` + `impl Vacia {}`.
7. `clase C(A, B): fin`: las bases sobreviven en AST/runtime; Python `(A, B)`, JS `extends A /* bases: A, B */`, Rust comentario.

### Programa futuro de referencia (no pasa hoy)

```cobra
clase Persona:
    metodo inicializar(este, nombre):
        atributo este nombre = nombre

    metodo saludar(este):
        imprimir "Hola", atributo este nombre
fin

var persona = Persona("Adolfo")
persona.saludar()
```

Resultado observable futuro: `Hola Adolfo`.

## 16. Matriz obligatoria de capacidades

`Sí*` significa que existe código aislado/manual pero la ruta pública no lo alcanza.

| Capacidad | Lexer | Parser | AST alcanzable | Runtime | Python | JS | Rust | Fuente E2E | Estado |
|---|---|---|---|---|---|---|---|---|---|
| clase | sí | sí | sí | sí | sí | sí | parcial | no POO completa | PARCIAL |
| clase vacía | sí | sí | sí | sí | roto | sí | sí | no cruzado | ROTO |
| inicializar | identificador | sí, destruye nombre | sí como `__init__` | no ejecuta constructor | solo por fuga | roto | roto | no | ROTO |
| este | identificador | sí posicional | sí | no liga `este` | no traduce | no traduce | no traduce | no | ROTO |
| atributo lectura | sí | sí | sí | sí* | emite punto | emite punto | parcial | no objeto invocable | PARCIAL |
| atributo escritura | sí | sí forma `atributo` | sí | sí*; semántico falla | emite punto | emite punto | emite punto inválido según receptor | no | ROTO |
| instancia | sí como llamada | no crea nodo | no | sí* sin ctor | coincidencia accidental | falta `new` | llamada inválida | no | ROTO |
| llamada método | sí | no | no | sí* | sí* | sí* | no completo | no | ROTO |
| retorno método | sí | sí | sí | sí* | sí | sí | parcial | bloqueado | PARCIAL |
| herencia simple | sí | sí | sí | sí* | sí | sí | comentario | bloqueado | PARCIAL |
| herencia múltiple | sí | sí | sí | sí* | sí | pierde bases | comentario | bloqueado | PARCIAL |
| override | sí | estructural | clases sí/llamada no | sí* | sí estructural | sí, una base | no | bloqueado | PARCIAL |
| superclase | identificador | no | no | no | no desde Cobra | no | no | no | NO SOPORTADO |
| atributo clase | sí | sí accidental | sí en lista errónea | rompe | casualmente | inválido | inválido | no | ACEPTACIÓN ACCIDENTAL |

## 17. Hallazgos

### POO-001 — P1 — Parser/cierre público
- **Reproductor:** programa objetivo exacto.
- **Actual:** el segundo `metodo` cae dentro del primero y falla.
- **Objetivo:** contrato de Task 42 parseable tal cual.
- **Causa:** cada método exige `fin`, mientras el contrato solo cierra la clase.
- **Dependencias:** decisión explícita de gramática 42A; requiere autorización futura para Parser.
- **Archivos:** `parser.py`, Libro/SPEC y futuros tests; ninguno modificado ahora.

### POO-002 — P1 — AST/neutralidad de constructor
- **Reproductor:** `metodo inicializar(este, nombre)` con cierres actuales.
- **Actual:** Parser guarda `nombre="__init__"`.
- **Objetivo:** identidad Cobra neutral y mapeo por backend.
- **Causa:** `ALIAS_METODOS_ESPECIALES` aplica dunders Python en frontend.
- **Dependencias:** modelo neutral antes de arreglar backends.
- **Archivos:** `core/utils.py`, `core/parser.py`, AST, visitors.

### POO-003 — P1 — referencia propia/binding
- **Reproductor:** `metodo f(este)` y acceso `atributo este nombre`.
- **Actual:** Parser conserva `este`, runtime define únicamente `self` y elimina el primer parámetro por posición; backends copian el lexema.
- **Objetivo:** ligar instancia Cobra y traducir solo al destino.
- **Causa:** convención runtime/backend acoplada a Python y sin receptor semántico.
- **Dependencias:** contrato neutral 42A/42B.
- **Archivos:** Parser/AST, `interpreter.py`, tres backends.

### POO-004 — P1 — instanciación inalcanzable
- **Reproductor:** `var persona = Persona("Adolfo")`.
- **Actual:** `NodoLlamadaFuncion`, no `NodoInstancia`; runtime no construye por esta ruta; JS pierde `new`, Rust no usa `::new`.
- **Objetivo:** resolución neutral de construcción y argumentos.
- **Causa:** llamada sintáctica no se resuelve semánticamente como clase.
- **Dependencias:** decidir resolución Parser vs semántica sin inventar sintaxis.
- **Archivos:** Parser/semántico/runtime/backends.

### POO-005 — P1 — llamada de método inalcanzable/corrupta
- **Reproductor:** `persona.saludar()` / `persona.cambiar_nombre("Ana")`.
- **Actual:** error para cero args; separación silenciosa en dos nodos para un arg; nunca `NodoLlamadaMetodo`.
- **Objetivo:** nodo único e invocación.
- **Causa:** `termino` procesa punto pero no postfix `(...)`.
- **Dependencias:** microtarea Parser autorizada, antes de E2E/herencia.
- **Archivos:** `parser.py`, optimizaciones, runtime/backends/tests.

### POO-006 — P1 — constructor runtime ausente
- **Reproductor:** `NodoInstancia` manual con clase que contiene `__init__`/`inicializar`.
- **Actual:** crea diccionario y no usa argumentos ni ejecuta método.
- **Objetivo:** ejecutar constructor con receptor y aridad correctos.
- **Causa:** `ejecutar_instancia` no hace lookup/invocación.
- **Dependencias:** POO-002/003/004.
- **Archivos:** `src/pcobra/core/interpreter.py`.

### POO-007 — P2 — aridad y nombre del receptor
- **Reproductor:** llamada manual con argumentos faltantes/sobrantes o primer parámetro distinto.
- **Actual:** `zip`, primer parámetro descartado, sin validación; define siempre `self`.
- **Objetivo:** binding `este` y error determinista de aridad.
- **Causa:** ruta de método diverge de `_ejecutar_descriptor_funcion_cobra`.
- **Dependencias:** POO-003/006.
- **Archivos:** runtime.

### POO-008 — P2 — Python clase vacía inválida
- **Reproductor:** `clase Vacia: fin`.
- **Actual:** `class Vacia:` sin `pass`.
- **Objetivo:** Python válido.
- **Causa:** `visit_clase` no emite cuerpo vacío.
- **Dependencias:** independiente tras contrato frontend.
- **Archivos:** `python_nodes/clase.py`.

### POO-009 — P2 — JS no adapta constructor/receptor/instancia
- **Reproductor:** clase con `inicializar`, `este`, y construcción desde fuente.
- **Actual:** `__init__(este,...)`; acceso `este.x`; `Persona(...)` sin `new`.
- **Objetivo:** `constructor(...)`, `this.x`, `new Persona(...)`.
- **Causa:** fuga AST y nodo de instancia inalcanzable.
- **Dependencias:** POO-002–005.
- **Archivos:** JS nodes y `to_js.py`.

### POO-010 — P2 — Rust POO incompleta
- **Reproductor:** constructor/herencia/método/atributo.
- **Actual:** struct sin campos, `__init__`, parámetros sin tipos/receptor, bases comentadas, `new` no definido, llamada método sin visitor completo.
- **Objetivo:** representación Rust coherente definida explícitamente, no copia de Python.
- **Causa:** backend estructural/esquelético.
- **Dependencias:** IR neutral y decisión de modelo Rust.
- **Archivos:** rust nodes y `to_rust.py`.

### POO-011 — P2 — herencia divergente y E2E bloqueado
- **Reproductor:** simple/múltiple y override desde fuente.
- **Actual:** metadata y lookup manual existen; JS pierde bases múltiples, Rust no implementa; invocación pública imposible.
- **Objetivo:** capacidad declarada con semántica compatible o diagnóstico explícito por backend.
- **Causa:** representación por backend y POO-004/005.
- **Dependencias:** llamadas/instancias primero.
- **Archivos:** semántico, runtime, backends.

### POO-012 — P2 — atributo de clase aceptado en contenedor incorrecto
- **Reproductor:** `clase C: var x = 1 fin`.
- **Actual:** asignación en `metodos`; runtime `AttributeError`; JS/Rust inválidos.
- **Objetivo:** rechazar con claridad o modelar explícitamente en futura tarea autorizada.
- **Causa:** cuerpo de clase acepta declaración genérica sin esquema.
- **Dependencias:** decisión contractual, posible Parser/AST.
- **Archivos:** Parser, AST, semántico/runtime/backends.

### POO-013 — P2 — incompatibilidad de identidad AST entre namespaces `core.ast_nodes` y `pcobra.core.ast_nodes`
- **Reproductor:** cuatro tests `test_to_python_objects.py`/`test_to_js_objects.py` y sondas en procesos frescos con `PYTHONPATH=src:src/pcobra`, variando el orden de importación.
- **Actual:** si se importa primero un transpilador por el namespace legado `cobra...`, `constant_folder` conserva una identidad `NodoAST` cargada antes de que los módulos visibles queden aliasados. Después, `NodoAST` visible de `core.ast_nodes is pcobra.core.ast_nodes` resulta `True`, pero es distinto del `NodoAST` ya capturado por `constant_folder`; el nodo satisface los dos primeros `isinstance` y no el tercero. El optimizador lanza `RuntimeError: Estructura AST inválida en optimización (constant_folder) en 'NodoInstancia': NodoInstancia` (análogamente para `NodoLlamadaMetodo`).
- **Contraprueba:** importando primero `core.ast_nodes` o `pcobra.core.ast_nodes`, las tres identidades coinciden y tanto instancias canónicas como legadas atraviesan `constant_folder`.
- **Objetivo:** identidad/compatibilidad única y estable, independiente del namespace y orden de importación.
- **Causa final:** incompatibilidad de identidad AST dependiente del orden/import namespace, no ausencia de casos/passthrough POO.
- **Dependencias:** reparar temprano; puede contaminar pruebas de frontend, runtime y backends.
- **No reparar mediante:** casos artificiales añadidos al optimizador.
- **Archivos:** inicialización/compatibilidad de namespaces AST; alcance exacto por determinar en 42B.

### POO-014 — P3 — documentación y ejemplos contradicen frontend/objetivo
- **Reproductor:** ejemplos citados en §13.
- **Actual:** `self`, `__init__`, punto asignable y cierres contradictorios.
- **Objetivo:** documentar solo el contrato verificado, después de implementarlo.
- **Causa:** deriva histórica.
- **Dependencias:** última tarea; jamás cambiar docs para ocultar fallos.
- **Archivos:** Libro, SPEC, README/examples.

### POO-015 — P3 — `super` inexistente
- **Reproductor:** búsqueda y cualquier intento `super...`.
- **Actual:** identificador ordinario sin semántica POO.
- **Objetivo:** no definido todavía; Task 42 prohíbe inventarlo.
- **Causa:** capacidad ausente.
- **Dependencias:** decisión normativa separada tras herencia básica.
- **Archivos:** por determinar; no tocar en 42A salvo decisión explícita.

### POO-016 — P2 — analizador semántico rechaza asignación de atributo
- **Reproductor:** clase con los cierres actualmente exigidos y cuerpo `atributo este nombre = nombre`.
- **Actual:** el Parser produce `NodoAsignacion(variable=NodoAtributo(...), ...)`; `visit_asignacion` llama `_validar_nombre(NodoAtributo)` y obtiene exactamente `TypeError: El nombre debe ser string, no <class 'pcobra.core.ast_nodes.NodoAtributo'>`.
- **Objetivo:** aceptar o validar semánticamente un destino `NodoAtributo` conforme al contrato POO sin debilitar la validación de asignaciones ordinarias.
- **Causa:** el analizador semántico presupone que todo destino de asignación es un nombre simple.
- **Dependencias:** atributos/semántico (42F), obligatoria antes del smoke E2E (42L).
- **Archivos:** analizador semántico y pruebas focales futuras; ninguno modificado en 42A.

## 18. Dependencias y secuencia propuesta

La reproducción de POO-013 confirma que el orden de importación puede contaminar pruebas posteriores. Por ello recibe una microtarea temprana y se renumera la secuencia:

1. **42A — contrato + roadmap + corrección de auditoría:** establecer `docs/POO_ROADMAP.md`; ningún cambio productivo.
2. **42B — compatibilidad de identidad AST:** normalizar `core.ast_nodes`, `pcobra.core.ast_nodes` y rutas relacionadas para que la identidad sea estable en ambos órdenes de importación.
3. **42C — neutralidad de constructor/receptor en AST/frontend + cierre de métodos:** conservar identidad Cobra y hacer parseable el contrato aprobado.
4. **42D — llamada de método postfix desde texto:** un único `NodoLlamadaMetodo` o IR neutral equivalente para 0/N argumentos.
5. **42E — resolución neutral de instanciación:** distinguir clase de función en una fase decidida explícitamente.
6. **42F — atributos + analizador semántico + cuerpo de clase:** incluye POO-012 y POO-016.
7. **42G — runtime: constructor, `este`, aridad y llamadas:** smoke desde fuente, no AST manual.
8. **42H — backend Python:** adaptaciones posteriores a la frontera neutral y clase vacía válida.
9. **42I — backend JavaScript:** `constructor`, `this`, `new` y llamadas.
10. **42J — backend Rust:** subconjunto idiomático explícito y diagnósticos para lo no soportado.
11. **42K — herencia y override:** solo después de la POO elemental; `super` queda fuera.
12. **42L — E2E contractual:** el programa futuro imprime exactamente `Hola Adolfo` en los destinos declarados.
13. **42M — documentación, SPEC, Libro y ejemplos:** únicamente tras comportamiento implementado y probado.

Cada microtarea debe contener reproductor, causa, autorización de capas sensibles, pruebas dirigidas y criterio de cierre. No se inicia ninguna aquí. El detalle contractual, los estados mantenibles y los invariantes están en `docs/POO_ROADMAP.md`.

## 19. Respuestas de cierre

1. `self` es hoy un identificador ordinario que documentación/tests usan como convención; runtime lo inyecta por nombre fijo.
2. `este` tokeniza y parsea como identificador, pero no recibe semántica runtime/backend.
3. `inicializar` se convierte en `__init__` dentro de `declaracion_metodo` (y también en declaraciones de función mediante el mismo mapa).
4. Sí: es **FUGA DE PYTHON AL AST COBRA**.
5. Sí, con cierres actuales por método y clase; no exactamente con el contrato objetivo.
6. No como instancia POO: desde fuente queda llamada de función.
7. No; `ejecutar_instancia` no ejecuta constructor.
8. El nodo de atributo es alcanzable; E2E sobre instancia pública no.
9. La forma `atributo objeto nombre = valor` es alcanzable; E2E POO no. El punto asignable se rechaza.
10. No; nunca se crea `NodoLlamadaMetodo` desde fuente.
11. Runtime manual define `self`, elimina el primer parámetro por posición y usa `zip`; no valida nombre/aridad.
12. Runtime/JS/Rust estructuralmente sí, Python genera sintaxis inválida; globalmente **ROTO**.
13. Parcial: metadata/runtime manual/Python/JS; no E2E, Rust no.
14. Parcial y divergente: runtime manual/Python conservan, JS/Rust no.
15. No: **NO SOPORTADO**.
16. Runtime manual tiene lookup favorable, pero desde fuente está bloqueado por llamada de método.
17. Desde texto: Clase, Método, Atributo; no Instancia ni LlamadaMétodo.
18. Instancia, llamada, ejecución de atributos, herencia y override dependen principalmente de AST manual.
19. Python hereda fugas pero se aproxima; JS carece de `constructor/this/new`; Rust es esquelético, sin herencia/campos/new coherente.
20. Los cambios mínimos son la secuencia 42A–42M: contrato/AST neutral, postfix e instancia, atributos, runtime, cada backend, herencia, E2E y por último docs.

**Cierre:** `Task 42 — AUDITORÍA COMPLETA`. **No** `POO — RESUELTA`.
