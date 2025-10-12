# Plan de ampliación de Cobra inspirado en lenguajes soportados

## Resumen ejecutivo consolidado

- **Biblioteca estándar**: expandir cadenas, colecciones, números y booleanos con APIs inspiradas en Python y en los demás lenguajes soportados para reducir brechas funcionales.
- **Modelo de ejecución**: introducir asincronía idiomática, decoradores utilitarios y un plan de migración gradual que preserve compatibilidad hacia atrás.
- **Computación cuántica holográfica**: definir un puente `Cobra ↔ Hololang` con decoradores de alto nivel, simulador local y controles de seguridad.
- **Interoperabilidad multilenguaje**: alinear las capacidades de Cobra con JavaScript, Rust, Go, Kotlin, Swift, R, Julia, Matlab, C/C++ y WebAssembly.
- **Documentación y adopción**: acompañar cada fase con manuales, notebooks, automatización de pruebas y seguimiento de indicadores.

## Objetivos generales

1. Incorporar funcionalidades idiomáticas presentes en Python que aún no existen en Cobra para fortalecer la biblioteca estándar y la expresividad del lenguaje.
2. Diseñar un puente de alto nivel que permita aprovechar decoradores y primitivas de computación cuántica holográfica, integrando Cobra con Hololang como capa de bajo nivel.
3. Extender la paridad de características con los demás lenguajes soportados por el transpilador (JavaScript, Rust, Go, Kotlin, etc.) para que los programas Cobra conserven semántica al migrar.
4. Definir un conjunto de tareas implementables y priorizadas que permitan desplegar estas mejoras de forma incremental.

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

## Puente holográfico para computación cuántica

### Objetivo
Crear un subsistema que conecte el código Cobra con rutinas cuánticas descritas en Hololang, permitiendo escribir algoritmos cuánticos de alto nivel mediante decoradores y abstracciones idiomáticas.

### Componentes propuestos
1. **Decorador `@cuantico`**: marca funciones Cobra que deben compilarse hacia kernels cuánticos en Hololang.
2. **Módulo `holo.cuantica`** con primitivas:
   - `prepara_estado(base, amplitudes)`
   - `aplica_puerta(nombre, qubits, parametros=None)`
   - `mide(qubits, repeticion=1)`
   - `superposicion(qubits)`
3. **Generador Hololang** que traduzca decoradores a bloques específicos (`hololang.quantum.kernel`).
4. **Administrador de recursos holográficos**: gestiona el envío de instrucciones a motores holográficos externos.
5. **Simulador local** para pruebas deterministas cuando no haya hardware holográfico disponible.
6. **API de resultados** (`ResultadoCuantico`) con métodos `probabilidades()`, `colapsa()`, `visualiza()`.

### Flujo de trabajo
1. El usuario declara `@cuantico` y utiliza primitivas `holo.cuantica` dentro de la función.
2. El transpilador detecta el decorador y transforma el AST Cobra en nodos Hololang especializados.
3. Hololang genera código intermedio holográfico (por ejemplo `hololang.qholo`) que puede ejecutarse en simuladores o hardware real.
4. Los resultados vuelven como objetos Cobra con métodos de post-procesamiento.

### Seguridad y sandboxing
- Lista blanca de puertas permitidas configurable por proyecto.
- Validación de topología (número máximo de qubits, profundidad de circuito).
- Registro de auditoría con metadatos para depuración.

---

## Inspiración en otros lenguajes del transpilador

### JavaScript / TypeScript
- **Promesas**: `promesa.resolver`, `promesa.rechazar`, `Promesa.todo`, `Promesa.carrera` para mapear con `Promise`.
- **Etiquetas de plantilla**: `plantilla_html` para integración con front-end.
- **Decorador `@observa_evento`** para enlazar eventos del DOM al transpilador JS.

### Rust
- **`resultado`** como enumeración (`exito`, `error`) con métodos `desempaqueta_or`, `mapa_error`.
- **Propiedad y préstamo**: anotaciones `prestamo(inmutable=True)` para recursos sensibles.
- **Macros ligeras**: `macro genera_getters(structura)`.

### Go
- **`rutina_ligera { ... }`** equivalente a goroutines.
- **Canales tipados**: interoperables con `canal.crea` y backends Go.
- **`defer`** como palabra reservada adicional.

### Kotlin / Swift
- **Extensiones de funciones** (`extiende Tipo { ... }`).
- **Corutinas estructuradas**: `alcance_corutina { ... }`.
- **Sistemas de sellado**: `clase sellada` para jerarquías restringidas.

### R / Julia / Matlab
- **Vectores columna y matrices** con operaciones `mapa`, `reduce`, `broadcast`.
- **`modulo.cientifico`** con utilidades estadísticas avanzadas (`media_geometrica`, `desviacion_robusta`).
- **Integración con notebooks** mediante `@grafica_inline`.

### WebAssembly / C / C++
- **Atributos de interoperabilidad** `@no_mangle`, `@externo("C")` para controlar nombres.
- **Estructuras empaquetadas** (`estructura empaquetada [alineacion=1]`).
- **Funciones intrínsecas** (`intrinseco.suma_vectorial`).

---

## Plan de tareas estructuradas

### Fase 1 · Fundamentos de la biblioteca
1. **Tarea F1.1 – Nuevas utilidades de cadenas**
   - Diseñar API `texto.*`, actualizar especificación léxica y casos de prueba.
   - Entregables: documentación en `docs/MANUAL_COBRA`, implementación en `src/cobra/std/texto.py` (nuevo módulo).
2. **Tarea F1.2 – Operaciones numéricas y booleanas**
   - Añadir métodos `clamp`, `bit_length`, `es_potencia_de_dos`, `xor`, `como_entero`.
   - Entregables: actualización de runtime, pruebas unitarias en `tests/runtime/test_numeros.py`.
3. **Tarea F1.3 – Colecciones avanzadas**
   - Implementar `lista.compacta`, `lista.desempaqueta`, `diccionario.*`.
   - Entregables: documentación, pruebas sobre listas/diccionarios.

### Fase 2 · Asincronía y decoradores
1. **Tarea F2.1 – Palabras clave `asincrono` y `espera`**
   - Extender gramática, parser y generador Hololang.
   - Entregables: RFC técnico, cobertura en `tests/frontend/async`.
2. **Tarea F2.2 – Librería de tareas**
   - Implementar `tarea.agrupar`, `tarea.tiempo_limite`, `canal.*`.
   - Entregables: módulo `std/async.py`, documentación y ejemplos.
3. **Tarea F2.3 – Decoradores utilitarios**
   - Incorporar `@memoriza`, `@valida_tipos`, `@despues`, `@asegura_contexto`.
   - Entregables: pruebas de integración y guía de uso.

### Fase 3 · Computación cuántica holográfica
1. **Tarea F3.1 – Especificación del decorador `@cuantico`**
   - Definir sintaxis, opciones y metadatos.
   - Entregables: documento de diseño, ejemplos en `notebooks/cuanticidad`.
2. **Tarea F3.2 – Backend Hololang cuántico**
   - Implementar traducción AST→Hololang con bloques `hololang.quantum`.
   - Entregables: módulo `src/cobra/transpiladores/hololang/cuanto.py`, pruebas de snapshots.
3. **Tarea F3.3 – Simulador y adaptadores**
   - Crear simulador local y conectores a hardware externo.
   - Entregables: CLI `cobra cuantico --simular`, documentación en `docs/cuanticidad.md`.
4. **Tarea F3.4 – Seguridad y auditoría**
   - Lista blanca de puertas, límites de recursos y bitácora.
   - Entregables: configuración en `cobra.toml`, reportes en `logs/cuantico.log`.

### Fase 4 · Integración con otros lenguajes
1. **Tarea F4.1 – Promesas y eventos JS**
   - Adaptar transpilador JS para mapear `promesa.*` y `@observa_evento`.
   - Entregables: ejemplos `examples/js/promesas.co`.
2. **Tarea F4.2 – Resultados estilo Rust**
   - Agregar tipo `resultado` y métodos asociados, garantizar traducción a Rust y Python.
   - Entregables: módulo `std/resultado.py`, pruebas cross-language.
3. **Tarea F4.3 – Goroutines y defer**
   - Introducir `rutina_ligera` y `defer`, asegurar correspondencia en Go y Python.
   - Entregables: especificación, casos de uso.
4. **Tarea F4.4 – Extensiones Kotlin/Swift**
   - Implementar `extiende Tipo { ... }`, `clase sellada` y corutinas estructuradas.
   - Entregables: actualización de la gramática y transpilers correspondientes.
5. **Tarea F4.5 – Interoperabilidad de bajo nivel**
   - Añadir atributos `@no_mangle`, `@externo`, estructuras empaquetadas e intrínsecos.
   - Entregables: pruebas en targets C/C++/WASM, documentación de FFI.

### Fase 5 · Documentación y adopción
1. **Tarea F5.1 – Manual y tutoriales**
   - Actualizar manuales (`docs/MANUAL_COBRA`, `docs/guia_basica.md`) y crear tutorial paso a paso.
2. **Tarea F5.2 – Ejemplos y notebooks**
   - Añadir notebooks para asincronía, cuántica y FFI.
3. **Tarea F5.3 – Automatización de pruebas**
   - Integrar suites en CI, añadir generadores de código para pruebas diferenciales.

---

## Consideraciones transversales
- Crear indicadores de cobertura específicos por fase para evaluar adopción.
- Mantener compatibilidad hacia atrás con alias y `deprecacion_programada`.
- Publicar RFCs previos a cambios en gramática o palabras reservadas.
- Coordinar con mantenedores de extensiones (VS Code, Jupyter) para actualizar el soporte sintáctico.

## Backlog de implementación práctica

El siguiente backlog descompone cada tarea macro en actividades implementables con entregables concretos
y facilita su incorporación como issues o historias dentro del repositorio.

### Fase 1 · Fundamentos de la biblioteca

| ID | Descripción | Cambios de código principales | Pruebas | Documentación | Dependencias |
| --- | --- | --- | --- | --- | --- |
| F1.1.a | Formalizar API de `texto` y actualizar especificaciones léxicas | Añadir interfaces en `docs/SPEC_COBRA.md` y esquemas en `src/cobra/std/__init__.py` | Revisión estática mediante `scripts/check_specs.py` | RFC breve en `docs/proposals` | Ninguna |
| F1.1.b | Implementar núcleo `texto.normaliza`, `texto.division_inteligente` y variantes | Nuevo módulo `src/cobra/std/texto.py`, registro en `cobra.mod` y `pyproject.toml` | Casos unitarios en `tests/std/test_texto.py` cubriendo unicode, mutaciones y errores | Ejemplos en `docs/MANUAL_COBRA.md` y `docs/guia_basica.md` | Requiere F1.1.a |
| F1.1.c | Integrar reemplazos con expresiones regulares | Incorporar dependencia opcional en `requirements.txt` si falta `regex`, exponer wrappers en runtime | Pruebas con patrones complejos y límites de reemplazo en `tests/std/test_texto_regex.py` | Nota de compatibilidad y ejemplos en `docs/standard_library/texto.md` | Depende de F1.1.b |
| F1.1.d | Añadir métodos destructivos (`!`) al compilador | Ajustar parser en `src/cobra/frontend/parser.py`, actualizar AST y código objetivo | Tests en `tests/frontend/test_mutaciones.py` asegurando generación correcta para todos los targets | Documentar semántica y advertencias en `MANUAL_COBRA` | Requiere F1.1.b |
| F1.2.a | Extender tipos numéricos con `clamp`, `bit_length`, `es_potencia_de_dos` | Modificar `src/cobra/runtime/numeros.py` y exponer intrínsecos | Tests paramétricos en `tests/runtime/test_numeros.py` | Tabla de métodos en `docs/standard_library/numeros.md` | Ninguna |
| F1.2.b | Añadir operaciones booleanas `xor`, `como_entero` | Actualizar `src/cobra/runtime/booleanos.py` y convertir booleanos a ints en transpilers | Casos cruzados en `tests/runtime/test_booleanos.py` | Actualizar cheatsheet en `docs/cheatsheet.tex` | Ninguna |
| F1.2.c | Sincronizar transpiladores con nuevas primitivas numéricas | Ajustar generadores en `src/cobra/transpiladores/{python,js,go}.py` | Tests de integración en `tests/transpilacion/test_numeros.py` verificando paridad | Añadir matriz comparativa en `docs/matriz_transpiladores.md` | Depende de F1.2.a |
| F1.3.a | Implementar utilidades de listas (`compacta`, `desempaqueta`) | Extender `src/cobra/runtime/listas.py` y helpers en `src/cobra/std/lista.py` | Nuevos tests en `tests/runtime/test_listas.py` | Manual estándar de colecciones | Ninguna |
| F1.3.b | Desarrollar mejoras para diccionarios (`obtener_clave`, `a_objeto`) | Modificar `src/cobra/runtime/diccionarios.py` y crear `SimpleNamespace` Cobra | Tests en `tests/runtime/test_diccionarios.py` y `tests/transpilacion/test_objetos.py` | Documentar en `docs/standard_library/diccionarios.md` | Requiere F1.3.a |
| F1.3.c | Integrar alias y compatibilidad en CLI | Añadir comandos de ejemplo en `examples/colecciones` y plantillas en `scripts/genera_ejemplos.py` | Tests de snapshot en `tests/examples/test_colecciones.py` | Tutorial en `docs/README.en.md` sección colecciones | Depende de F1.3.a |

### Fase 2 · Asincronía y decoradores

| ID | Descripción | Cambios de código principales | Pruebas | Documentación | Dependencias |
| --- | --- | --- | --- | --- | --- |
| F2.1.a | Añadir tokens `asincrono` y `espera` a la gramática | Actualizar `docs/gramatica.ebnf`, lexer y parser en `src/cobra/frontend` | Tests sintácticos en `tests/frontend/async/test_tokens.py` | Nota de versión en `CHANGELOG.md` | Ninguna |
| F2.1.b | Emitir AST y bytecode base para funciones async | Ajustar nodos en `src/cobra/frontend/nodos.py` y generadores en `src/cobra/backend` | Tests de AST en `tests/frontend/async/test_ast.py` y snapshots | Documentar arquitectura en `docs/frontend/asincronia.md` | Requiere F2.1.a |
| F2.1.c | Conectar transpilers con async/await | Actualizar `src/cobra/transpiladores/{python,js,go,hololang}.py` | Tests end-to-end en `tests/transpilacion/async/test_corutinas.py` | Añadir guía en `docs/proposals/asincronia.md` | Requiere F2.1.b |
| F2.2.a | Crear módulo `std/async.py` con `tarea.agrupar`, `tarea.tiempo_limite` | Nuevo archivo `src/cobra/std/asyncio.py` integrando event loop | Tests concurrentes en `tests/std/test_async.py` con `pytest.mark.asyncio` | Ejemplos en `examples/async/` y tutorial | Requiere F2.1.c |
| F2.2.b | Implementar canales (`canal.crea`, `canal.enviar`, `canal.recibir`) | Extender runtime y adaptadores en `src/cobra/runtime/async_canal.py` | Pruebas de estrés con `tests/std/test_canal.py` | Documentar patrones de productor-consumidor | Depende de F2.2.a |
| F2.3.a | Incorporar decoradores `@memoriza`, `@valida_tipos` | Añadir módulo `src/cobra/std/decoradores/cache.py` y validadores | Tests de funcionalidad en `tests/std/test_decoradores_cache.py` | Manual de decoradores en `docs/standard_library/decoradores.md` | Requiere F1.1 y F1.2 |
| F2.3.b | Implementar `@despues`, `@asegura_contexto` con scheduler | Crear scheduler simple en `src/cobra/runtime/scheduler.py` | Tests temporales en `tests/runtime/test_scheduler.py` usando relojes simulados | Añadir advertencias de bloqueo en manual | Depende de F2.2.a |

### Fase 3 · Computación cuántica holográfica

| ID | Descripción | Cambios de código principales | Pruebas | Documentación | Dependencias |
| --- | --- | --- | --- | --- | --- |
| F3.1.a | Definir metadatos del decorador `@cuantico` | Añadir anotaciones en `docs/proposals/cuanticidad.md` y esquema en `src/cobra/frontend/atributos.py` | Validaciones de análisis estático en `tests/frontend/quantum/test_validacion.py` | FAQ inicial en `docs/cuanticidad.md` | Requiere F2.3 |
| F3.1.b | Crear AST especializado para bloques cuánticos | Nuevos nodos en `src/cobra/frontend/nodos_cuanticos.py` y visitas en `src/cobra/backend/visitas_cuanticas.py` | Tests de construcción en `tests/frontend/quantum/test_ast.py` | Sección técnica en `docs/arquitectura_parser_transpiladores.md` | Depende de F3.1.a |
| F3.2.a | Generar código Hololang desde decoradores | Módulo `src/cobra/transpiladores/hololang/cuanto.py` con integración en `cobra.mod` | Snapshot tests con `tests/transpilacion/quantum/test_hololang.py` | Manual de interoperabilidad en `docs/standard_library/holo.md` | Depende de F3.1.b |
| F3.2.b | Implementar adaptadores a motores holográficos | Conector en `src/cobra/runtime/quantum/cliente.py`, configuración en `cobra.toml` | Tests con simulador falso en `tests/runtime/quantum/test_cliente.py` | Guía de despliegue en `docs/cuanticidad.md` | Depende de F3.2.a |
| F3.3.a | Desarrollar simulador local determinista | Añadir `src/cobra/runtime/quantum/simulador.py` y CLI `cobra cuantico --simular` | Tests deterministas en `tests/runtime/quantum/test_simulador.py` | Tutorial paso a paso en `notebooks/cuanticidad/simulador.ipynb` | Depende de F3.2.b |
| F3.4.a | Incorporar controles de seguridad y auditoría | Middleware en `src/cobra/runtime/quantum/seguridad.py`, logging en `logs/cuantico.log` | Tests de límites en `tests/runtime/quantum/test_seguridad.py` | Documentar políticas en `docs/cuanticidad.md` | Depende de F3.3.a |

### Fase 4 · Integración con otros lenguajes

| ID | Descripción | Cambios de código principales | Pruebas | Documentación | Dependencias |
| --- | --- | --- | --- | --- | --- |
| F4.1.a | Mapear `promesa.*` y `@observa_evento` en backend JS | Ajustar `src/cobra/transpiladores/js/promesas.py` y runtime JS | Tests de integración en `tests/transpilacion/js/test_promesas.py` | Guía en `docs/interfaces.md` | Requiere F2.2 |
| F4.1.b | Exponer plantillas etiquetadas `plantilla_html` | Añadir helper en `src/cobra/std/html.py` y transpilar a template strings | Tests de snapshots en `tests/transpilacion/js/test_html.py` | Ejemplos en `examples/js/` | Depende de F4.1.a |
| F4.2.a | Implementar tipo `resultado` en runtime común | Archivo `src/cobra/runtime/resultado.py` con métodos `mapa_error`, `desempaqueta_or` | Tests cruzados en `tests/runtime/test_resultado.py` y transpilación comparativa | Documentar patrón en `docs/standard_library/resultado.md` | Ninguna |
| F4.2.b | Sincronizar transpiladores (Rust, Python) con `resultado` | Ajustar `src/cobra/transpiladores/{rust,python}.py` y generadores de enums | Tests golden en `tests/transpilacion/rust/test_resultado.rs` | Tabla de equivalencias en `docs/matriz_transpiladores.md` | Depende de F4.2.a |
| F4.3.a | Añadir `rutina_ligera` y `defer` al parser | Modificar gramática y AST en `src/cobra/frontend` | Tests de sintaxis y semántica en `tests/frontend/go/test_rutinas.py` | Documentar patrón en `docs/frontend/go.md` | Requiere F2.1 |
| F4.3.b | Integrar goroutines y `defer` en backends Go y Python | Actualizar `src/cobra/transpiladores/{go,python}.py` y runtime | Tests end-to-end en `tests/transpilacion/go/test_defer.go` | Ejemplos en `examples/go/` | Depende de F4.3.a |
| F4.4.a | Implementar extensiones de tipo (`extiende Tipo { ... }`) | Añadir soporte al parser y a generadores Kotlin/Swift | Tests en `tests/transpilacion/kotlin/test_extensiones.kt` | Documentar en `docs/frontend/kotlin.md` | Requiere F2.1 |
| F4.4.b | Añadir `clase sellada` y corutinas estructuradas | Ajustar runtime y transpilers Kotlin/Swift | Tests de jerarquías en `tests/transpilacion/kotlin/test_clases_selladas.kt` | Tutorial en `docs/frontend/kotlin.md` | Depende de F4.4.a |
| F4.5.a | Agregar atributos `@no_mangle`, `@externo` | Extender parser y generadores C/C++/WASM | Tests de FFI en `tests/transpilacion/c/test_externo.c` | Documentar en `docs/limitaciones_cpp_sandbox.md` | Ninguna |
| F4.5.b | Soporte para estructuras empaquetadas e intrínsecos | Ajustar representación de tipos en `src/cobra/backend/tipos.py` y runtime wasm | Tests binarios en `tests/transpilacion/wasm/test_intrinsecos.wat` | Guía en `docs/arquitectura_parser_transpiladores.md` | Depende de F4.5.a |

### Fase 5 · Documentación y adopción

| ID | Descripción | Cambios de código principales | Pruebas | Documentación | Dependencias |
| --- | --- | --- | --- | --- | --- |
| F5.1.a | Actualizar manuales con nuevas APIs | Revisar `docs/MANUAL_COBRA.md`, `docs/guia_basica.md`, `docs/README.en.md` | Validación con `make docs` y revisión ortográfica | Plantillas de snippets en `docs/standard_library` | Depende de fases 1-4 |
| F5.1.b | Crear tutorial guiado paso a paso | Notebook `notebooks/tutorial_novedades.ipynb` y script `examples/tutorial/main.co` | Ejecución manual en CI y `pytest -k tutorial` | Entrada de blog en `docs/blog_minilenguaje.md` | Depende de F5.1.a |
| F5.2.a | Publicar notebooks demostrativos | Añadir `notebooks/async.ipynb`, `notebooks/cuanticidad.ipynb`, `notebooks/ffi.ipynb` | Tests `pytest -k notebook-smoke` con `papermill` | Documentar en `docs/notebooks/README.md` | Depende de fases respectivas |
| F5.3.a | Integrar suites de pruebas nuevas al CI | Actualizar `Makefile`, workflows en `.github/workflows/ci.yml` y `pyproject.toml` | Ejecutar pipeline local `make ci` | Añadir sección en `CONTRIBUTING.md` | Depende de F1-F4 |
| F5.3.b | Crear generadores para pruebas diferenciales | Scripts en `scripts/genera_pruebas_diferenciales.py` | Tests de regresión en `tests/scripts/test_generadores.py` | Documentar proceso en `docs/coverage.md` | Depende de F5.3.a |


## Estrategia de conciliación con la rama principal

- **Resolución aplicada**: se consolidó este plan con la versión base asegurando que los objetivos generales y las fases del backlog queden integradas en un único documento sin secciones duplicadas.
- **Política de merges**: los archivos de `docs/proposals` pueden fusionarse usando la estrategia `union` para concatenar cambios complementarios en lugar de generar conflictos manuales.
- **Guía operativa**:
  1. Actualizar la rama de trabajo con `git fetch` y `git merge origin/main` antes de continuar.
  2. Si aparece un conflicto en este archivo, aceptar ambos bloques y revisar que las tablas mantengan el orden por fase.
  3. Ejecutar la revisión ortográfica o `make lint-docs` (cuando esté disponible) antes de confirmar los cambios.


