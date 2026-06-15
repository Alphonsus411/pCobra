# Libro de Programación con Cobra

> **Estado del documento: Principal**
>
> Ruta pedagógica oficial de Cobra (de nivel inicial a avanzado).

Este libro es la **guía pedagógica principal** para aprender Cobra de forma progresiva.
Si buscas una vista breve, consulta el [Resumen rápido](guia_basica.md).
Si necesitas detalle normativo y comportamiento de runtime, usa primero la [Referencia técnica canónica](MANUAL_COBRA.md) y, si lo prefieres, su [versión RST autogenerada](MANUAL_COBRA.rst).

## Índice

1. [Qué es Cobra y cómo pensar en su ecosistema](#1-qué-es-cobra-y-cómo-pensar-en-su-ecosistema)
2. [Primeros pasos](#2-primeros-pasos)
3. [Sintaxis base del lenguaje por dominios](#3-sintaxis-base-del-lenguaje-por-dominios)
4. [Control de flujo](#4-control-de-flujo)
5. [Funciones y reutilización](#5-funciones-y-reutilización)
6. [Estructuras de datos](#6-estructuras-de-datos)
7. [Módulos, imports y organización de código](#7-módulos-imports-y-organización-de-código)
8. [Manejo de errores y validaciones semánticas](#8-manejo-de-errores-y-validaciones-semánticas)
9. [Concurrencia y asincronía](#9-concurrencia-y-asincronía)
10. [CLI de Cobra para desarrollo diario](#10-cli-de-cobra-para-desarrollo-diario)
11. [Transpilación, targets y compatibilidad](#11-transpilación-targets-y-compatibilidad)
12. [Biblioteca estándar (corelibs / standard library)](#12-biblioteca-estándar-corelibs--standard-library)
13. [Buenas prácticas de arquitectura en proyectos Cobra](#13-buenas-prácticas-de-arquitectura-en-proyectos-cobra)
14. [Rendimiento, profiling y optimización](#14-rendimiento-profiling-y-optimización)
15. [Seguridad y sandbox](#15-seguridad-y-sandbox)
16. [Pruebas, calidad y mantenimiento](#16-pruebas-calidad-y-mantenimiento)
17. [De cero a avanzado en orden recomendado](#17-de-cero-a-avanzado-en-orden-recomendado)
18. [Apéndice: checklist de publicación de un proyecto Cobra](#18-apéndice-checklist-de-publicación-de-un-proyecto-cobra)
19. [Checklist editorial del libro](#19-checklist-editorial-del-libro)

---

## 1) Qué es Cobra y cómo pensar en su ecosistema

Cobra es un lenguaje y ecosistema de tooling orientado a:

- escribir código legible en español,
- ejecutar con intérprete,
- y/o transpilar a múltiples targets.

La forma práctica de trabajar en Cobra es:

1. Diseñar la lógica en `.cobra`.
2. Validar sintaxis/semántica localmente.
3. Ejecutar pruebas.
4. Transpilar según el target de despliegue.

---

## 2) Primeros pasos

### 2.1 Hola mundo

```cobra
imprimir("Hola, Cobra")
```

### 2.2 Variables y tipos básicos

```cobra
nombre = "Ada"
edad = 28
activo = verdadero
altura = 1.68
```

### 2.3 Comentarios

```cobra
# Comentario de una línea
```

---

## 3) Sintaxis base del lenguaje por dominios

<!-- BEGIN: AUTO-SYNTAX-INDEX -->
### Índice de sintaxis (autogenerado)

#### Tokens léxicos

- `CADENA`
- `ENTERO`
- `FLOTANTE`
- `IDENTIFICADOR`

#### Palabras reservadas (gramática + SPEC)

- `!`
- `&&`
- `(`
- `)`
- `*`
- `+`
- `,`
- `-`
- `/`
- `:`
- `<`
- `=`
- `==`
- `>`
- `@`
- `BOOLEANO`
- `CADENA`
- `ENTERO`
- `FLOTANTE`
- `[`
- `]`
- `_`
- `afirmar`
- `asincronico`
- `atributo`
- `capturar`
- `case`
- `catch`
- `clase`
- `como`
- `con`
- `continuar`
- `desde`
- `eliminar`
- `elseif`
- `enumeracion`
- `esperar`
- `estructura`
- `fin`
- `finalmente`
- `func`
- `garantia`
- `global`
- `graficar`
- `guard`
- `hilo`
- `holobit`
- `import`
- `imprimir`
- `in`
- `intentar`
- `lambda`
- `lanzar`
- `macro`
- `metodo`
- `mientras`
- `no`
- `nolocal`
- `o`
- `para`
- `pasar`
- `proyectar`
- `registro`
- `retorno`
- `romper`
- `si`
- `sino`
- `sino si`
- `switch`
- `transformar`
- `usar`
- `var`
- `variable`
- `y`
- `{`
- `||`
- `}`

#### Estructuras

- `funcion`
- `funcion_asincronica`
- `clase`
- `condicional`
- `bucle_mientras`
- `bucle_para`
- `switch`
- `try_catch`
- `with_stmt`
- `macro`
- `garantia`

#### Expresiones

- `coincidencia`
- `valor (operador valor)*`

**Valores permitidos en expresiones**
- `"None"`
- `"Some" "(" expr ")"`
- `"esperar" valor`
- `CADENA`
- `ENTERO`
- `FLOTANTE`
- `IDENTIFICADOR`
- `holobit`
- `lambda`
- `llamada`

#### Sentencias

- `asignacion`
- `bucle_mientras`
- `bucle_para`
- `clase`
- `condicional`
- `expr`
- `funcion`
- `funcion_asincronica`
- `garantia`
- `hilo`
- `importacion`
- `impresion`
- `llamada`
- `macro`
- `option`
- `retorno`
- `switch`
- `try_catch`
- `usar`
- `with_stmt`
<!-- END: AUTO-SYNTAX-INDEX -->

### Tablas rápidas: token/estructura → uso práctico

| Token/estructura | Uso práctico |
|---|---|
| `IDENTIFICADOR` | Nombrar variables, funciones, clases y módulos. |
| `CADENA`, `ENTERO`, `FLOTANTE`, `BOOLEANO` | Definir literales de datos comunes. |
| `funcion`, `funcion_asincronica` | Encapsular lógica reutilizable, con o sin `esperar`. |
| `condicional`, `bucle_mientras`, `bucle_para` | Controlar flujo según reglas o recorridos. |
| `try_catch` | Capturar y manejar errores controlables. |
| `clase` | Modelar estado + comportamiento orientado a objetos. |
| `usar`, `importacion` | Reutilizar módulos/proyectos. |
| `macro`, `garantia` | Metaprogramación y contratos/aseguramiento. |

| Estructura | Uso práctico |
|---|---|
| Expresiones | Calcular valores (`a + b`, llamadas, lambdas, `esperar`). |
| Sentencias | Ejecutar acciones con efecto (`imprimir`, `retorno`, asignaciones). |
| Bloques | Agrupar instrucciones con el mismo alcance semántico. |

### 3.1 Léxico

**Definición corta:** conjunto de tokens válidos (identificadores, literales, operadores y reservadas).

**Sintaxis formal simplificada:**

```text
IDENTIFICADOR := [a-zA-Z_][a-zA-Z0-9_]*
LITERAL := CADENA | ENTERO | FLOTANTE | BOOLEANO
TOKEN := IDENTIFICADOR | LITERAL | OPERADOR | RESERVADA
```

**Ejemplos:**

```cobra
usuario_id = 42
mensaje = "Hola"
activo = verdadero
```

```cobra
precio = 19.99
impuesto = 0.21
```

**Anti-ejemplo frecuente:** usar identificadores con espacios.

```cobra
# Incorrecto
mi variable = 10
```

**Compatibilidad por backend:** el BackEnd oficial público está compuesto solo por `python`, `javascript` y `rust`. Evita depender de detalles de targets no oficiales.

### 3.2 Expresiones

**Definición corta:** combinaciones de valores y operadores que producen un resultado.

**Sintaxis formal simplificada:**

```text
expr := valor (operador valor)*
valor := LITERAL | IDENTIFICADOR | llamada | "(" expr ")"
```

**Ejemplos:**

```cobra
total = (subtotal + impuesto) * 1.05
```

```cobra
permitido = edad >= 18 y activo
```

```cobra
saludo = f"Hola {nombre}"
```

**Anti-ejemplo frecuente:** mezclar tipos incompatibles sin conversión explícita.

```cobra
# Incorrecto
resultado = "10" + 5
```

**Compatibilidad por backend:** operadores aritméticos/lógicos son estables; interpolación `f"..."` puede traducirse distinto según target.

### 3.3 Sentencias

**Definición corta:** instrucciones ejecutables que modifican estado o controlan flujo.

**Sintaxis formal simplificada:**

```text
sentencia := asignacion | impresion | retorno | condicional | bucle | llamada
asignacion := IDENTIFICADOR "=" expr
```

**Ejemplos:**

```cobra
x = 10
imprimir(x)
```

```cobra
retornar "ok"
```

**Anti-ejemplo frecuente:** usar `retornar` fuera de función.

**Compatibilidad por backend:** sentencias base estables; `imprimir` puede mapear a stdout con formato diferente por plataforma.

### 3.4 Funciones

**Definición corta:** bloques parametrizables para reutilizar comportamiento.

**Sintaxis formal simplificada:**

```text
funcion := "funcion" IDENTIFICADOR "(" [params] ")" ":" bloque
params := IDENTIFICADOR ("," IDENTIFICADOR)*
```

**Ejemplos:**

```cobra
funcion saludar(nombre):
    retornar f"Hola, {nombre}"
```

```cobra
funcion potencia(base, exponente = 2):
    retornar base ** exponente
```

```cobra
funcion aplicar(valor, fn):
    retornar fn(valor)
```

**Anti-ejemplo frecuente:** funciones largas con I/O y lógica de dominio mezcladas.

**Compatibilidad por backend:** estable; closures/lambdas complejas pueden degradar rendimiento en backends embebidos.

### 3.5 Clases

**Definición corta:** mecanismo OO para agrupar atributos y métodos.

**Sintaxis formal simplificada:**

```text
clase := "clase" IDENTIFICADOR ":" bloque
metodo := "metodo" IDENTIFICADOR "(" [params] ")" ":" bloque
```

**Ejemplos:**

```cobra
clase Cuenta:
    atributo saldo

    metodo depositar(monto):
        saldo = saldo + monto
```

```cobra
clase Usuario:
    metodo __init__(nombre):
        self.nombre = nombre
```

**Anti-ejemplo frecuente:** exponer estado mutable sin invariantes.

**Compatibilidad por backend:** clases básicas estables; herencia múltiple puede variar en calidad de transpiliación según backend.

### 3.6 Módulos

**Definición corta:** unidades de organización y reutilización de código.

**Contrato vigente de `usar` (sin cambiar lexer/parser):**

- **Sintaxis implementada actual (restricción del parser):** `usar "numero"` (siempre con cadena).
- **Semántica objetivo oficial:** importación plana de funciones del módulo Cobra cargado, por ejemplo `es_finito(...)` **sin prefijo**.

**Sintaxis formal simplificada:**

```text
usar_stmt := "usar" CADENA  # sintaxis implementada actualmente por parser
```

**Ejemplos:**

```cobra
usar "texto"
usar "numero"
```

```cobra
usar "mi_modulo.utilidades"
```

Ejemplo canónico de adaptación (actual):

```cobra
# entrada (válida por parser actual)
usar "numero"
# uso plano esperado
imprimir(es_finito(10))
```

### 3.7 Errores

**Definición corta:** estrategias para reportar y recuperar fallos en tiempo de ejecución.

**Sintaxis formal simplificada:**

```text
try_catch := "intentar" ":" bloque "capturar" IDENTIFICADOR ":" bloque
lanzar := "lanzar" expr
```

**Ejemplos:**

```cobra
intentar:
    dato = convertir_entero(entrada)
capturar e:
    imprimir("Entrada inválida")
```

```cobra
funcion dividir(a, b):
    si b == 0:
        lanzar "División por cero"
    retornar a / b
```

**Anti-ejemplo frecuente:** capturar error genérico y silenciarlo sin log/contexto.

**Compatibilidad por backend:** modelos de excepción varían; en backends mínimos, priorizar validaciones explícitas.

### 3.8 Concurrencia

**Definición corta:** ejecución coordinada de tareas asíncronas o en hilos.

**Sintaxis formal simplificada:**

```text
funcion_async := "asincronico" "funcion" IDENTIFICADOR "(" [params] ")" ":" bloque
await_expr := "esperar" valor
hilo_stmt := "hilo" IDENTIFICADOR
```

**Ejemplos:**

```cobra
asincronico funcion obtener_datos(url):
    retornar esperar cliente.get(url)
```

```cobra
asincronico funcion main():
    respuesta = esperar obtener_datos("https://api")
    imprimir(respuesta)
```

**Anti-ejemplo frecuente:** bloqueo síncrono dentro de función asincrónica.

**Compatibilidad por backend:** soporte async completo en backend Python; en otros targets revisar disponibilidad de event loop.

### 3.9 Contrato para sugerencias automáticas en GUI/IA

Las herramientas de GUI, asistentes de IA o acciones de corrección automática pueden sugerir cambios sobre código Cobra, pero **no pueden ampliar la sintaxis del lenguaje por su cuenta**. Toda recomendación debe cumplir este contrato antes de mostrarse como corrección aplicable:

1. **Validación de entrada:** el código original se tokeniza con `Lexer` y se parsea con `Parser`. Si el fragmento de entrada no puede validarse, la herramienta debe informar el error en vez de inventar una corrección sintáctica.
2. **Sintaxis existente:** la sugerencia no debe introducir tokens, palabras reservadas, operadores o construcciones ausentes del parser vigente. Si una forma no aparece en el índice de sintaxis ni es aceptada por `Parser`, queda fuera de las recomendaciones automáticas.
3. **Trazabilidad al Libro:** cada recomendación debe mapearse a una regla concreta de este Libro, citando la sección aplicable (por ejemplo, `§3.3 Sentencias`, `§3.4 Funciones` o `§3.6 Módulos`).
4. **Regresión obligatoria:** por cada recomendación nueva se añade un caso válido y uno inválido en `tests/gui/` o `tests/integration/`; además, el fragmento sugerido debe tener una prueba que confirme que `Parser` lo acepta.

Recomendaciones autorizadas actualmente:

| Recomendación | Regla del Libro | Fragmento sugerido que debe aceptar `Parser` | Forma inválida cubierta por regresión |
|---|---|---|---|
| Usar `retorno` dentro de funciones. | `§3.3 Sentencias` y `§3.4 Funciones`. | `func saludar(nombre): retorno nombre fin` | `retornar nombre` |
| Usar `usar` sin alias `como` y con importación plana. | `§3.6 Módulos`. | `usar "numero"` seguido de `es_finito(10)` | `usar "numero" como numero` |
| Declarar funciones con `func` o `definir`. | `§3.4 Funciones`. | `func calcular_total(a, b): retorno a + b fin` | `funcion calcular_total(a, b): ...` |

> Nota editorial: si en el futuro el parser incorpora una construcción nueva, primero debe actualizarse el índice de sintaxis y la regla correspondiente del Libro; solo después puede añadirse una recomendación automática para esa construcción.

### 3.10 Decorators

**Definición corta:** anotaciones (`@`) para extender funciones/clases sin modificar su cuerpo.

**Sintaxis formal simplificada:**

```text
decorador := "@" IDENTIFICADOR ["(" [args] ")"]
declaracion := decorador* funcion | decorador* clase
```

**Ejemplos:**

```cobra
@memoizar
funcion fib(n):
    si n < 2:
        retornar n
    retornar fib(n-1) + fib(n-2)
```

```cobra
@reintentar(intentos = 3)
funcion descargar(url):
    retornar cliente.get(url)
```

**Anti-ejemplo frecuente:** encadenar decorators con efectos secundarios no documentados.

**Compatibilidad por backend:** decorators dependen de capacidades de metaprogramación del target; validar en `build` por backend.

### 3.11 Macros

**Definición corta:** transformación de código antes o durante fases de compilación/transpilación.

**Sintaxis formal simplificada:**

```text
macro := "macro" IDENTIFICADOR "(" [params] ")" ":" bloque
```

**Ejemplos:**

```cobra
macro traza(expr):
    imprimir(f"TRACE => {expr}")
```

```cobra
traza(usuario_id)
```

**Anti-ejemplo frecuente:** usar macros para lógica de negocio en vez de abstracciones normales.

**Compatibilidad por backend:** comportamiento depende del pipeline de transpiler; mantener macros pequeñas y deterministas.

### 3.12 Patrones avanzados

**Definición corta:** combinaciones de constructos para resolver problemas complejos de forma mantenible.

**Sintaxis formal simplificada:**

```text
patron := composicion_funcional | guard_clauses | pipelines_modulares | reintentos_controlados
```

**Ejemplos:**

```cobra
funcion crear_usuario(cmd):
    si no cmd.email:
        retornar error("email requerido")
    retornar repositorio.guardar(cmd)
```

```cobra
resultado = datos
    .filtrar(funcion(x): retornar x.activo)
    .mapear(funcion(x): retornar x.email)
```

```cobra
asincronico funcion publicar_evento(e):
    retornar esperar reintentar_async(funcion(): retornar bus.emitir(e), intentos = 3)
```

**Anti-ejemplo frecuente:** sobreingeniería (introducir patrón sin dolor real del dominio).

**Compatibilidad por backend:** patrones son conceptuales; verificar disponibilidad de APIs (`asincrono`, `decoradores`) según target.

---

## 4) Control de flujo

### 4.1 Condicionales

```cobra
si temperatura > 30:
    imprimir("Hace calor")
sino_si temperatura > 20:
    imprimir("Clima templado")
sino:
    imprimir("Hace frío")
```

### 4.2 Bucles `mientras`

```cobra
i = 0
mientras i < 3:
    imprimir(i)
    i = i + 1
```

### 4.3 Bucles por colección

```cobra
nombres = ["Ana", "Luis", "Marta"]
para nombre en nombres:
    imprimir(nombre)
```

### 4.4 Control de iteración

```cobra
para n en [1,2,3,4,5]:
    si n == 3:
        continuar
    si n == 5:
        romper
    imprimir(n)
```

---

## 5) Funciones y reutilización

### 5.1 Declaración de funciones

```cobra
funcion saludar(nombre):
    retornar f"Hola, {nombre}"
```

### 5.2 Parámetros con valores por defecto

```cobra
funcion potencia(base, exponente = 2):
    retornar base ** exponente
```

### 5.3 Funciones puras y efectos secundarios

Recomendación:

- Mantén funciones puras para lógica de negocio.
- Aísla I/O (archivo/red/consola) en capas externas.

### 5.4 Composición

```cobra
funcion normalizar(nombre):
    retornar texto.recortar(nombre).minusculas()

funcion registrar_usuario(nombre):
    limpio = normalizar(nombre)
    imprimir(f"Registrado: {limpio}")
```

---

## 6) Estructuras de datos

### 6.1 Listas

```cobra
numeros = [10, 20, 30]
numeros.agregar(40)
imprimir(numeros[0])
```

### 6.2 Diccionarios

```cobra
usuario = {
  "id": 1,
  "nombre": "Ada",
  "activo": verdadero
}

imprimir(usuario["nombre"])
```

### 6.3 Tuplas y estructuras inmutables

Úsalas para datos que no deben mutar durante la ejecución.

### 6.4 Transformaciones comunes

- Filtrar
- Mapear
- Reducir
- Ordenar

```cobra
pares = numeros.filtrar(funcion(x): retornar x % 2 == 0)
```

---

## 7) Módulos, imports y organización de código

### 7.1 Importar módulos

```cobra
usar "texto"
usar "numero"
```

### 7.2 Estructura recomendada

```text
mi_proyecto/
  src/
    app.cobra
    dominio/
    infraestructura/
  tests/
  cobra.mod
```

### 7.3 Reglas de diseño

- Cada módulo debe tener una responsabilidad clara.
- Evita dependencias cíclicas.
- Expón API pública mínima.

---

## 8) Manejo de errores y validaciones semánticas

### 8.1 Errores esperables

- Entrada inválida
- Recursos no disponibles
- Fallos de tipo/forma de datos

### 8.2 Estrategia recomendada

- Valida temprano.
- Falla rápido con mensaje claro.
- Registra contexto de error.

```cobra
funcion dividir(a, b):
    si b == 0:
        error("División por cero")
    retornar a / b
```

---

## 9) Concurrencia y asincronía

Cobra incluye módulos de soporte para flujos asíncronos y coordinación.

### 9.1 Cuándo usar asincronía

- I/O de red
- operaciones de archivo de alta latencia
- integración con servicios externos

### 9.2 Patrones

- fan-out / fan-in
- colas de trabajo
- timeouts y reintentos

---

## 10) CLI de Cobra para desarrollo diario

La CLI de Cobra es la herramienta principal para interactuar con el lenguaje. Ofrece comandos para ejecutar, construir, probar y gestionar módulos.

Los comandos públicos disponibles son:

*   ``run``: Ejecuta un archivo Cobra.
*   ``build``: Compila un proyecto Cobra.
*   ``test``: Ejecuta las pruebas de un proyecto Cobra.
*   ``mod``: Gestiona los módulos y dependencias del proyecto.
*   ``repl``: Inicia una sesión interactiva (Read-Eval-Print Loop).

Para más detalles sobre cada comando, puedes usar ``cobra <comando> --help``.

### 10.1 IDLE gráfico con gestión de archivos

Cobra incluye un entorno de desarrollo integrado (IDLE) gráfico basado en Flet, que permite escribir, ejecutar y transpilar código de forma interactiva. Este IDLE ha sido mejorado con las siguientes funcionalidades:

*   **Editor de código:** Un área principal para escribir y editar tu código Cobra.
*   **Gestión de archivos:**
    *   **Guardar:** Guarda el archivo actual en su ubicación.
    *   **Guardar como:** Permite guardar el contenido del editor en una nueva ubicación o con un nuevo nombre.
    *   **Árbol de directorios:** Una vista lateral que muestra la estructura de archivos y carpetas de tu proyecto. Puedes hacer clic en los archivos `.co` o `.cobra` para cargarlos directamente en el editor.
*   **Ejecución y transpilación:**
    *   **Selector de target:** Elige el lenguaje de destino (Python, JavaScript, Rust) para la transpilación.
    *   **Switch de transpilación:** Alterna entre ejecutar el código directamente o transpilarlo al lenguaje seleccionado.
    *   **Botón "Ejecutar":** Ejecuta el código Cobra o lo transpila, mostrando la salida o el código generado en el área de resultados.
*   **Sugerencias de código (Agix):**
    *   **Botón "Sugerencias (Agix)":** Utiliza la librería opcional `agix` para analizar tu código y ofrecer sugerencias de mejora o corrección tipográfica, basándose en las mejores prácticas del "Libro de Programación principal". Las sugerencias se muestran en el área de salida.

Para iniciar el IDLE, usa el comando ``cobra gui``.

.. code-block:: bash

   cobra gui

Flujo mínimo sugerido:

```bash
cobra run src/app.cobra
cobra build src/app.cobra
cobra test src/app.cobra
cobra mod list
```

Comandos útiles adicionales (según el setup del proyecto):

- `cobra test`
- `cobra plugins`
- `cobra docs`
- `cobra profile`

### Comandos legacy y migración

Si vienes de comandos legacy, migra al contrato público `run/build/test/mod` y revisa la
guía de transición en [`docs/migracion_cli_unificada.md`](migracion_cli_unificada.md).

---

## 11) Transpilación, targets y compatibilidad

El BackEnd oficial público está compuesto solo por `python`, `javascript` y `rust`. Esos tres targets forman el contrato de usuario para `cobra build` y la documentación pública.

### 11.1 Regla práctica

- Para máxima estabilidad operativa: usa los targets oficiales `python`, `javascript` y `rust`.

### 11.2 Estrategia de release

1. Validar sintaxis.
2. Ejecutar pruebas de comportamiento.
3. Transpilar.
4. Probar artefacto generado en entorno limpio.

---

## 12) Biblioteca estándar (corelibs / standard library)

<!-- BEGIN: AUTO-STDLIB-INDEX -->
### Índice de módulos y funciones de `standard_library` (autogenerado)

- **`archivo`** (4 funciones) → `docs/standard_library/archivo.md`
  - API: `adjuntar`, `escribir`, `existe`, `leer`
- **`asincrono`** (5 funciones) → `docs/standard_library/asincrono.md`
  - API: `ejecutar_en_hilo`, `grupo_tareas`, `limitar_tiempo`, `proteger_tarea`, `reintentar_async`
- **`datos`** (32 funciones) → `docs/standard_library/datos.md`
  - API: `a_listas`, `agrupar_y_resumir`, `calcular_percentiles`, `combinar_tablas`, `correlacion_pearson`, `correlacion_spearman`, `de_listas`, `describir`, ...
- **`decoradores`** (9 funciones) → `docs/standard_library/decoradores.md`
  - API: `dataclase`, `depreciado`, `despachar_por_tipo`, `memoizar`, `orden_total`, `reintentar`, `reintentar_async`, `sincronizar`, ...
- **`fecha`** (3 funciones) → `docs/standard_library/fecha.md`
  - API: `formatear`, `hoy`, `sumar_dias`
- **`interfaz`** (18 funciones) → `docs/standard_library/interfaz.md`
  - API: `barra_progreso`, `estado_temporal`, `grupo_consola`, `imprimir_aviso`, `iniciar_gui`, `iniciar_gui_idle`, `limpiar_consola`, `mostrar_arbol`, ...
- **`lista`** (12 funciones) → `docs/standard_library/lista.md`
  - API: `cabeza`, `chunk`, `cola`, `combinar`, `descartar_mientras`, `longitud`, `mapear_aplanado`, `mapear_seguro`, ...
- **`logica`** (25 funciones) → `docs/standard_library/logica.md`
  - API: `alguna`, `coalesce`, `condicional`, `conjuncion`, `conteo_verdaderos`, `diferencia_simetrica`, `disyuncion`, `entonces`, ...
- **`numero`** (22 funciones) → `docs/standard_library/numero.md`
  - API: `coeficiente_variacion`, `combinaciones`, `copiar_signo`, `cuartiles`, `distancia_euclidiana`, `envolver_modular`, `es_finito`, `es_infinito`, ...
- **`texto`** (51 funciones) → `docs/standard_library/texto.md`
  - API: `a_camel`, `a_snake`, `acortar_texto`, `centrar_texto`, `codificar`, `contar_subcadena`, `decodificar`, `desindentar_texto`, ...
- **`util`** (4 funciones) → `docs/standard_library/util.md`
  - API: `es_nulo`, `es_vacio`, `rel`, `repetir`
<!-- END: AUTO-STDLIB-INDEX -->

Áreas típicas:

- `texto`
- `numero`
- `logica`
- `archivo`
- `red`
- `tiempo`
- `coleccion`
- `seguridad`
- `asincrono`
- `sistema`

### 12.1 Criterios de uso

- Prioriza APIs estables.
- Evita depender de detalles internos no documentados.
- Encapsula adaptadores para facilitar migraciones entre versiones.

---

## 13) Buenas prácticas de arquitectura en proyectos Cobra

### 13.1 Patrón por capas

- Presentación/CLI
- Aplicación (casos de uso)
- Dominio
- Infraestructura

### 13.2 Convenciones recomendadas

- Nombres de funciones en verbo + intención.
- Módulos pequeños y cohesionados.
- Contratos explícitos en fronteras entre módulos.

### 13.3 Antipatrones

- Módulos “Dios” con cientos de responsabilidades.
- Lógica de dominio mezclada con consola/red.
- Duplicación de utilidades sin módulo común.

---

## 14) Rendimiento, profiling y optimización

### 14.1 Orden recomendado

1. Mide.
2. Detecta cuellos de botella.
3. Optimiza lo crítico.
4. Re-mide.

### 14.2 Técnicas comunes

- reducir asignaciones innecesarias,
- eliminar recomputación,
- aprovechar estructuras de datos adecuadas,
- cachear resultados deterministas costosos.

---

## 15) Seguridad y sandbox

- Ejecuta código no confiable en sandbox.
- Limita acceso a filesystem/red según política.
- Restringe imports peligrosos.
- Audita dependencias y plugins.

Checklist rápido:

- [ ] Entradas validadas.
- [ ] Acceso a secretos minimizado.
- [ ] Logs sin datos sensibles.
- [ ] Timeouts configurados.

---

## 16) Pruebas, calidad y mantenimiento

### 16.1 Pirámide de pruebas

- Unitarias (base)
- Integración (medio)
- E2E/CLI (puntas críticas)

### 16.2 Calidad continua

- lint + formato
- validación de sintaxis Cobra
- suite de tests en CI
- control de regresiones de docs y ejemplos

---

## 17) De cero a avanzado en orden recomendado

Ruta práctica (ejecuta cada bloque antes de pasar al siguiente):

### 17.1 Cero → base sintáctica

1. `examples/tutorial_basico/hola_mundo.co`
2. `examples/tutorial_basico/README.md`
3. `examples/tutorial_basico/compile_manual.py`

Objetivo: dominar ejecución mínima, literales, impresión y ciclo editar-ejecutar.

### 17.2 Base → features del lenguaje

1. `examples/features/feature_base/minimal.co`
2. `examples/features/README.md`

Objetivo: practicar estructuras canónicas que luego aparecen en proyectos reales.

### 17.3 Features → avanzado por dominio

1. `examples/avanzados/funciones/factorial_recursivo.co`
2. `examples/avanzados/funciones/utilidades.co`
3. `examples/avanzados/clases/persona.co`
4. `examples/avanzados/clases/herencia_multiple.co`
5. `examples/avanzados/control_flujo/README.md`

Objetivo: integrar funciones, clases, reutilización y control de flujo no trivial.

### 17.4 Cierre recomendado

- Repetir la ruta ejecutando `cobra run` en cada ejemplo.
- Documentar dudas por constructo (léxico/expresión/sentencia/función/etc.).
- Revisar backend objetivo antes de transpilar (`cobra build`).

---

## 18) Apéndice: checklist de publicación de un proyecto Cobra

- [ ] `cobra run` sobre smoke tests de `src/`.
- [ ] tests pasando en CI.
- [ ] documentación de uso actualizada.
- [ ] ejemplos ejecutables y verificados.
- [ ] matriz de targets revisada para el release.


## 19) Checklist editorial del libro

Checklist obligatorio de cierre para futuras ediciones:

- [ ] Cada constructo documentado tiene **ejemplo mínimo ejecutable**.
- [ ] Cada constructo incluye **nota de alcance** (qué cubre y qué no cubre).
- [ ] Cada subcapítulo de dominio incluye definición, sintaxis, ejemplos y anti-ejemplo.
- [ ] Las notas de compatibilidad por backend están indicadas cuando aplica.
- [ ] Los ejemplos referenciados en `examples/` existen y son trazables desde esta guía.

---

## Nota de consolidación documental

Este libro sustituye como guía de aprendizaje principal a documentos introductorios parciales o dispersos. Para especificación técnica detallada y política de targets, complementa con:

- `docs/SPEC_COBRA.md`
- `docs/especificacion_tecnica.md`
- `docs/targets_policy.md`
- `docs/MANUAL_COBRA.md`


### Contrato de `usar` en REPL (estricto)

En REPL, `usar` aplica una política **estricta** y distinta del runtime general:

- Solo se aceptan módulos oficiales Cobra definidos en el mapa canónico `REPL_COBRA_MODULE_MAP` (por ejemplo `numero`, `texto`, `logica`, etc.).
- Si el módulo solicitado no está en ese mapa, se aborta antes de cualquier import externo o instalación con `PermissionError("módulos externos no soportados en REPL")`.
- En REPL no se permite fallback de instalación con `pip` bajo ninguna condición.
- La inyección de símbolos es atómica: si falla la validación/carga, no queda estado parcial en el contexto interactivo.

Fuera del REPL, el runtime general mantiene su política de whitelist y sus mecanismos de resolución/instalación configurables.
