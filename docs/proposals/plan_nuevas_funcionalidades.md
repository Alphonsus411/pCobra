# Plan vigente de nuevas funcionalidades

> **Estado:** propuesta activa.
>
> **Alcance de política:** este plan **no amplía `OFFICIAL_TARGETS`** ni introduce nuevos targets públicos de salida. Cualquier referencia a pipelines internos, investigación o material retirado debe mantenerse fuera de esta propuesta activa o enlazarse con etiquetas visibles de **experimental**, **histórico** o **fuera de política**.
>
> **Contexto archivado:** la antigua línea de trabajo sobre un pipeline holográfico interno se conserva únicamente como material **experimental · fuera de política** dentro de `docs/experimental/`.

## Resumen ejecutivo consolidado

- **Biblioteca estándar**: ampliar textos, colecciones, números y booleanos con APIs inspiradas en Python y compatibles con la arquitectura actual.
- **Modelo de ejecución**: introducir asincronía idiomática, decoradores utilitarios y utilidades concurrentes sin cambiar la política pública de targets.
- **Interoperabilidad multilenguaje**: priorizar mejoras que mantengan paridad semántica dentro de los 8 targets oficiales (`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`).
- **Documentación y adopción**: acompañar cada fase con manuales, notebooks, automatización de pruebas y seguimiento de indicadores.

## Objetivos generales

1. Incorporar funcionalidades idiomáticas presentes en Python que aún no existen en Cobra para fortalecer la biblioteca estándar y la expresividad del lenguaje.
2. Mejorar la paridad de características entre los targets oficiales del transpilador para que los programas Cobra conserven semántica al migrar.
3. Definir tareas implementables y priorizadas que puedan desplegarse de forma incremental sin abrir nuevos targets públicos.
4. Mantener toda la documentación de la propuesta alineada con la estructura actual `src/pcobra/cobra/...`.

## Guardas de política para esta propuesta

### Targets públicos que sí forman parte del plan vigente

Los únicos targets públicos de salida contemplados por esta propuesta son:

- `python`
- `rust`
- `javascript`
- `wasm`
- `go`
- `cpp`
- `java`
- `asm`

### Referencias explícitamente fuera de alcance

- No se propone ningún pipeline interno **experimental** como target público ni como ampliación de `OFFICIAL_TARGETS`.
- No se propone `llvm`, `latex` ni otros artefactos experimentales como targets públicos.
- No deben reaparecer aliases legacy del backend JavaScript en ejemplos, tablas o rutas de implementación.

---

## Ampliaciones inspiradas en Python

### Manipulación avanzada de textos y cadenas
- **`texto.normaliza(modo="nfc")`**: normalización Unicode configurable (`nfc`, `nfd`, `nfkc`, `nfkd`).
- **`texto.remplaza_patron(patron, reemplazo, maximo=None)`**: sustitución con soporte de expresiones regulares y límite opcional.
- **`texto.division_inteligente(separador=None, maximo=-1)`**: equivalente a `str.split` pero con heurísticas para espacios múltiples.
- **`texto.partes(separador, incluir_separador=False)`**: inspirado en `re.split` para conservar delimitadores cuando se requiera.
- **`texto.formatea(plantilla, **datos)`**: motor de plantillas tipo `str.format`, compatible con diccionarios Cobra.
- **`texto.fstring(expresion)`**: evaluación segura de expresiones interpoladas, útil para migrar f-strings.
- **Métodos in-place (`texto.mayusculas!`, `texto.minusculas!`)** que optimicen mutaciones sin reasignar la variable.

### Funciones adicionales sobre colecciones
- **`lista.compacta()`**: elimina valores nulos o vacíos (equivalente a `filter(None, secuencia)`).
- **`lista.desempaqueta(niveles=1)`**: aplana listas anidadas, inspirado en `itertools.chain.from_iterable`.
- **`diccionario.obtener_clave(predicado)`**: retorna la primera clave que cumpla un predicado dado.
- **`diccionario.a_objeto()`**: conversión a un registro accesible por atributos (similar a `types.SimpleNamespace`).

### Números y booleanos
- **`entero.clamp(minimo, maximo)`**: recorta el valor dentro de un rango.
- **`entero.bit_length()`** y **`entero.es_potencia_de_dos()`**: utilidades de análisis binario.
- **`decimal.redondea(bandas=0, modo="mitad_arriba")`**: redondeo configurable (ceiling, floor, bankers).
- **`booleano.xor(otro)`** y **`booleano.como_entero()`**: alineadas con operaciones bit a bit.

### Asincronía y concurrencia
- Nuevas palabras clave: **`asincrono`** (definición) y **`espera`** (suspensión) alineadas con `async/await`.
- **`tarea.agrupar(*corutinas, politica="primero")`**: combinador inspirado en `asyncio.gather`.
- **`tarea.tiempo_limite(duracion)`**: contexto para cancelar tareas.
- **`canal.crea(buffer=0)`**, **`canal.enviar(valor)`**, **`canal.recibir()`**: canales estilo `asyncio.Queue` para componer pipelines.

### Decoradores listos para usar
- **`@memoriza(maximo=None)`**: cache de resultados tipo `functools.lru_cache`.
- **`@valida_tipos`**: verificación en tiempo de ejecución similar a `typing.runtime_checkable`.
- **`@despues(segundos)`**: agenda ejecución diferida.
- **`@asegura_contexto(recurso)`**: inyecta apertura/cierre de recursos alineado con `contextlib`.

### Métodos especiales y protocolos
- **`__entrar__` / `__salir__`**: protocolo de manejadores de contexto.
- **`__iterador__`, `__siguiente__`**: soporte nativo para iteradores personalizados.
- **`__async_iterador__`, `__async_siguiente__`**: versión asíncrona.
- **`__destructurar__(indices)`**: permite controlar el desempaquetado múltiple.
- **`__matmul__(otro)`**: operador matemático para productos matriciales.

---

## Inspiración en otros lenguajes oficiales del transpilador

### JavaScript
- **Promesas**: `promesa.resolver`, `promesa.rechazar`, `Promesa.todo`, `Promesa.carrera` para mapear con `Promise`.
- **Etiquetas de plantilla**: `plantilla_html` para integración con front-end.
- **Decorador `@observa_evento`** para enlazar eventos del DOM al backend `javascript`.

### Rust
- **`resultado`** como enumeración (`exito`, `error`) con métodos `desempaqueta_or`, `mapa_error`.
- **Propiedad y préstamo**: anotaciones `prestamo(inmutable=True)` para recursos sensibles.
- **Macros ligeras**: `macro genera_getters(structura)`.

### Go
- **`rutina_ligera { ... }`** equivalente a goroutines.
- **Canales tipados**: interoperables con `canal.crea` y backend `go`.
- **`defer`** como palabra reservada adicional.

### Java
- **Paridad orientada a objetos**: clases, interfaces y excepciones con semántica consistente.
- **Anotaciones de interoperabilidad** para bibliotecas Java existentes.
- **Optimización de colecciones** para `ArrayList`/`HashMap` en generación de código.

### ASM
- **Intrínsecos controlados** para operaciones numéricas críticas.
- **Macros de bajo nivel** orientadas a depuración de runtime en `asm`.
- **Perfiles de salida** para diagnósticos y tamaño mínimo.

### WebAssembly / `cpp`
- **Atributos de interoperabilidad** `@no_mangle`, `@externo` para controlar nombres.
- **Estructuras empaquetadas** (`estructura empaquetada [alineacion=1]`).
- **Funciones intrínsecas** (`intrinseco.suma_vectorial`).

---

## Plan de tareas estructuradas

### Fase 1 · Fundamentos de la biblioteca
1. **Tarea F1.1 – Nuevas utilidades de cadenas**
   - Diseñar API `texto.*`, actualizar especificación léxica y casos de prueba.
   - Entregables: documentación en `docs/MANUAL_COBRA.md`, implementación en `src/pcobra/cobra/core/` y módulos de soporte asociados bajo `src/pcobra/cobra/`.
2. **Tarea F1.2 – Operaciones numéricas y booleanas**
   - Añadir métodos `clamp`, `bit_length`, `es_potencia_de_dos`, `xor`, `como_entero`.
   - Entregables: actualización de runtime/semántica vigente y pruebas unitarias.
3. **Tarea F1.3 – Colecciones avanzadas**
   - Implementar `lista.compacta`, `lista.desempaqueta`, `diccionario.*`.
   - Entregables: documentación y pruebas sobre listas/diccionarios.

### Fase 2 · Asincronía y decoradores
1. **Tarea F2.1 – Palabras clave `asincrono` y `espera`**
   - Extender gramática, parser y transpiladores oficiales vigentes.
   - Entregables: RFC técnico y cobertura en pruebas.
2. **Tarea F2.2 – Librería de tareas**
   - Implementar `tarea.agrupar`, `tarea.tiempo_limite`, `canal.*`.
   - Entregables: módulos de soporte bajo `src/pcobra/cobra/` y ejemplos.
3. **Tarea F2.3 – Decoradores utilitarios**
   - Incorporar `@memoriza`, `@valida_tipos`, `@despues`, `@asegura_contexto`.
   - Entregables: pruebas de integración y guía de uso.

### Fase 3 · Integración con otros lenguajes oficiales
1. **Tarea F3.1 – Promesas y eventos en `javascript`**
   - Adaptar el backend `javascript` para mapear `promesa.*` y `@observa_evento`.
   - Entregables: ejemplos, documentación y pruebas de integración.
2. **Tarea F3.2 – Resultados estilo Rust**
   - Agregar tipo `resultado` y métodos asociados, garantizando traducción a `rust` y `python`.
   - Entregables: módulos compartidos, pruebas cross-language y documentación.
3. **Tarea F3.3 – Goroutines y `defer`**
   - Introducir `rutina_ligera` y `defer`, asegurando correspondencia en `go` y `python` cuando aplique.
   - Entregables: especificación y casos de uso.
4. **Tarea F3.4 – Paridad Java y ASM**
   - Consolidar clases, interfaces, excepciones y utilidades de bajo nivel en `java` y `asm`.
   - Entregables: actualización de gramática, runtime y transpiladores.
5. **Tarea F3.5 – Interoperabilidad de bajo nivel**
   - Añadir atributos `@no_mangle`, `@externo`, estructuras empaquetadas e intrínsecos.
   - Entregables: pruebas en `cpp`/`wasm` y documentación de FFI.

### Fase 4 · Documentación y adopción
1. **Tarea F4.1 – Manual y tutoriales**
   - Actualizar manuales (`docs/MANUAL_COBRA.md`, `docs/guia_basica.md`) y crear tutorial paso a paso.
2. **Tarea F4.2 – Ejemplos y notebooks**
   - Añadir notebooks para asincronía, FFI y nuevas APIs de biblioteca estándar.
3. **Tarea F4.3 – Automatización de pruebas**
   - Integrar suites en CI y añadir generadores de código para pruebas diferenciales.

---

## Consideraciones transversales
- Crear indicadores de cobertura específicos por fase para evaluar adopción.
- Mantener compatibilidad hacia atrás con alias y `deprecacion_programada`, pero sin exponer aliases legacy en UX pública.
- Publicar RFCs previos a cambios en gramática o palabras reservadas.
- Coordinar con mantenedores de extensiones (VS Code, Jupyter) para actualizar el soporte sintáctico.
- Cualquier referencia futura a pipelines internos no oficiales, LLVM, LaTeX u otros artefactos fuera de política debe mantenerse fuera de esta propuesta activa y marcarse de forma visible como **experimental**, **histórica** o **fuera de política**.

## Backlog de implementación práctica

El siguiente backlog descompone cada tarea macro en actividades implementables con entregables concretos y facilita su incorporación como issues o historias dentro del repositorio.

### Fase 1 · Fundamentos de la biblioteca

| ID | Descripción | Cambios de código principales | Pruebas | Documentación | Dependencias |
| --- | --- | --- | --- | --- | --- |
| F1.1.a | Formalizar API de `texto` y actualizar especificaciones léxicas | Añadir interfaces en `docs/SPEC_COBRA.md` y adaptar módulos de núcleo bajo `src/pcobra/cobra/` | Revisión estática mediante scripts de especificación | RFC breve en `docs/proposals/` | Ninguna |
| F1.1.b | Implementar núcleo `texto.normaliza`, `texto.division_inteligente` y variantes | Nuevos módulos bajo `src/pcobra/cobra/` y registro en la configuración vigente del proyecto | Casos unitarios cubriendo unicode, mutaciones y errores | Ejemplos en `docs/MANUAL_COBRA.md` y `docs/guia_basica.md` | Requiere F1.1.a |
| F1.1.c | Integrar reemplazos con expresiones regulares | Incorporar dependencia opcional si hiciera falta y exponer wrappers en runtime/stdlib vigente | Pruebas con patrones complejos y límites de reemplazo | Nota de compatibilidad y ejemplos en `docs/standard_library/texto.md` | Depende de F1.1.b |
| F1.1.d | Añadir métodos destructivos (`!`) al compilador | Ajustar parser en `src/pcobra/cobra/core/parser.py` y estructuras AST/código objetivo asociadas | Tests asegurando generación correcta para todos los targets oficiales | Documentar semántica y advertencias en `docs/MANUAL_COBRA.md` | Requiere F1.1.b |
| F1.2.a | Extender tipos numéricos con `clamp`, `bit_length`, `es_potencia_de_dos` | Modificar runtime/semántica vigente bajo `src/pcobra/cobra/` y exponer intrínsecos | Tests paramétricos en runtime | Tabla de métodos en `docs/standard_library/numero.md` | Ninguna |
| F1.2.b | Añadir operaciones booleanas `xor`, `como_entero` | Actualizar helpers semánticos y compatibilidad entre transpilers | Casos cruzados de comportamiento | Actualizar cheatsheet en `docs/cheatsheet.tex` | Ninguna |
| F1.2.c | Sincronizar transpilers con nuevas primitivas numéricas | Ajustar generadores en `src/pcobra/cobra/transpilers/transpiler/{to_python.py,to_js.py,to_go.py}` | Tests de integración verificando paridad | Añadir matriz comparativa en `docs/matriz_transpiladores.md` | Depende de F1.2.a |
| F1.3.a | Implementar utilidades de listas (`compacta`, `desempaqueta`) | Extender runtime y helpers de biblioteca estándar bajo `src/pcobra/cobra/` | Nuevos tests de listas | Manual estándar de colecciones | Ninguna |
| F1.3.b | Desarrollar mejoras para diccionarios (`obtener_clave`, `a_objeto`) | Modificar runtime y crear una abstracción de namespace Cobra | Tests de runtime y transpilación asociados | Documentar en `docs/standard_library/datos.md` | Requiere F1.3.a |
| F1.3.c | Integrar ejemplos y compatibilidad en CLI | Añadir comandos/plantillas de ejemplo sin introducir nombres de target no canónicos | Tests de snapshot y smoke tests | Tutorial en `docs/README.en.md` sección colecciones | Depende de F1.3.a |

### Fase 2 · Asincronía y decoradores

| ID | Descripción | Cambios de código principales | Pruebas | Documentación | Dependencias |
| --- | --- | --- | --- | --- | --- |
| F2.1.a | Añadir tokens `asincrono` y `espera` a la gramática | Actualizar `docs/gramatica.ebnf`, lexer y parser bajo `src/pcobra/cobra/core/` | Tests sintácticos para tokens async | Nota de versión en `CHANGELOG.md` | Ninguna |
| F2.1.b | Emitir AST base para funciones async | Ajustar nodos/árbol interno y generadores oficiales | Tests de AST y snapshots | Documentar arquitectura en `docs/frontend/arquitectura.rst` o equivalente | Requiere F2.1.a |
| F2.1.c | Conectar transpilers con async/await | Actualizar `src/pcobra/cobra/transpilers/transpiler/{to_python.py,to_js.py,to_go.py}` sin añadir nuevos targets públicos | Tests end-to-end de corutinas | Añadir guía en `docs/proposals/` si procede | Requiere F2.1.b |
| F2.2.a | Crear soporte de tareas con `tarea.agrupar` y `tarea.tiempo_limite` | Nuevos módulos bajo `src/pcobra/cobra/` integrando el event loop vigente | Tests concurrentes | Ejemplos y tutorial | Requiere F2.1.c |
| F2.2.b | Implementar canales (`canal.crea`, `canal.enviar`, `canal.recibir`) | Extender runtime y adaptadores bajo `src/pcobra/cobra/` | Pruebas de estrés | Documentar patrones de productor-consumidor | Depende de F2.2.a |
| F2.3.a | Incorporar decoradores `@memoriza`, `@valida_tipos` | Añadir soporte compartido bajo `src/pcobra/cobra/` y validadores | Tests de funcionalidad | Manual de decoradores en `docs/standard_library/decoradores.md` | Requiere F1.1 y F1.2 |
| F2.3.b | Implementar `@despues`, `@asegura_contexto` con scheduler | Crear scheduler simple y adaptadores | Tests temporales usando relojes simulados | Añadir advertencias de bloqueo en manual | Depende de F2.2.a |

### Fase 3 · Integración con otros lenguajes oficiales

| ID | Descripción | Cambios de código principales | Pruebas | Documentación | Dependencias |
| --- | --- | --- | --- | --- | --- |
| F3.1.a | Mapear `promesa.*` y `@observa_evento` en backend `javascript` | Ajustar `src/pcobra/cobra/transpilers/transpiler/to_js.py` y helpers de nodos `js_nodes/` | Tests de integración de promesas | Guía en `docs/interfaces.md` | Requiere F2.2 |
| F3.1.b | Exponer plantillas etiquetadas `plantilla_html` | Añadir helper compartido y transpilar a template strings | Tests de snapshots | Ejemplos front-end | Depende de F3.1.a |
| F3.2.a | Implementar tipo `resultado` en runtime común | Archivo y helpers bajo `src/pcobra/cobra/` con métodos `mapa_error`, `desempaqueta_or` | Tests cruzados y comparativos | Documentar patrón en `docs/standard_library/logica.md` o ruta equivalente | Ninguna |
| F3.2.b | Sincronizar transpilers (`rust`, `python`) con `resultado` | Ajustar `src/pcobra/cobra/transpilers/transpiler/{to_rust.py,to_python.py}` | Tests golden y comparativos | Tabla de equivalencias en `docs/matriz_transpiladores.md` | Depende de F3.2.a |
| F3.3.a | Añadir `rutina_ligera` y `defer` al parser | Modificar gramática y AST bajo `src/pcobra/cobra/core/` | Tests de sintaxis y semántica | Documentar patrón en documentación de Go cuando exista | Requiere F2.1 |
| F3.3.b | Integrar goroutines y `defer` en backends `go` y `python` | Actualizar `src/pcobra/cobra/transpilers/transpiler/{to_go.py,to_python.py}` y runtime asociado | Tests end-to-end | Ejemplos en `examples/go/` si se incorporan | Depende de F3.3.a |
| F3.4.a | Fortalecer clases/interfaces para backend `java` | Ajustar parser y generador en `src/pcobra/cobra/transpilers/transpiler/` | Tests de integración Java | Documentar en `docs/frontend/` cuando proceda | Requiere F2.1 |
| F3.4.b | Mejorar salida `asm` para diagnóstico y rendimiento | Ajustar backend `asm` y runtime mínimo | Tests de transpilación ASM | Tutorial técnico en `docs/frontend/` si se incorpora | Depende de F3.4.a |
| F3.5.a | Agregar atributos `@no_mangle`, `@externo` | Extender parser y generadores `cpp`/`wasm` | Tests de FFI | Documentar en `docs/limitaciones_cpp_sandbox.md` | Ninguna |
| F3.5.b | Soporte para estructuras empaquetadas e intrínsecos | Ajustar representación de tipos y runtime `wasm` | Tests binarios/semánticos | Guía en `docs/arquitectura_parser_transpiladores.md` | Depende de F3.5.a |

### Fase 4 · Documentación y adopción

| ID | Descripción | Cambios de código principales | Pruebas | Documentación | Dependencias |
| --- | --- | --- | --- | --- | --- |
| F4.1.a | Actualizar manuales con nuevas APIs | Revisar `docs/MANUAL_COBRA.md`, `docs/guia_basica.md`, `docs/README.en.md` | Validación con la pipeline de docs y revisión ortográfica | Plantillas de snippets en `docs/standard_library/` | Depende de fases 1-3 |
| F4.1.b | Crear tutorial guiado paso a paso | Notebook y ejemplo principal de novedades | Ejecución manual en CI y smoke tests | Entrada de blog o guía interna | Depende de F4.1.a |
| F4.2.a | Añadir suites diferenciales en CI | Extender scripts/CI para verificar semántica en los 8 targets oficiales | Ejecución automatizada por matriz | Documentar criterios de cobertura | Depende de fases 1-3 |
