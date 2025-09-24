# Plan de ampliación de Cobra inspirado en lenguajes soportados

## Objetivos generales

1. Incorporar funcionalidades idiomáticas presentes en Python que aún no existen en Cobra para fortalecer la biblioteca estándar y la expresividad del lenguaje.
2. Diseñar un puente de alto nivel que permita aprovechar decoradores y primitivas de computación cuántica holográfica, integrando Cobra con Hololang como capa de bajo nivel.
3. Extender la paridad de características con los demás lenguajes soportados por el transpilador (JavaScript, Rust, Go, Kotlin, etc.) para que los programas Cobra conserven semántica al migrar.
4. Definir un conjunto de tareas implementables y priorizadas que permitan desplegar estas mejoras de forma incremental.

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

