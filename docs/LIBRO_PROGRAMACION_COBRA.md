# Libro de Programación con Cobra

> **Estado del documento: Principal**
>
> Ruta pedagógica oficial de Cobra (de nivel inicial a avanzado).

Este libro es la **guía pedagógica principal** para aprender Cobra de forma progresiva.
Si buscas una vista breve, consulta el [Resumen rápido](guia_basica.md).
Si necesitas detalle normativo y comportamiento de runtime, usa la [Referencia técnica](MANUAL_COBRA.md) y su [versión RST](MANUAL_COBRA.rst).

## Índice

1. [Qué es Cobra y cómo pensar en su ecosistema](#1-qué-es-cobra-y-cómo-pensar-en-su-ecosistema)
2. [Primeros pasos](#2-primeros-pasos)
3. [Sintaxis base del lenguaje](#3-sintaxis-base-del-lenguaje)
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
17. [Roadmap de aprendizaje por niveles](#17-roadmap-de-aprendizaje-por-niveles)
18. [Apéndice: checklist de publicación de un proyecto Cobra](#18-apéndice-checklist-de-publicación-de-un-proyecto-cobra)

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

## 3) Sintaxis base del lenguaje

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
- `enum`
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
- `throw`
- `transformar`
- `try`
- `usar`
- `var`
- `variable`
- `y`
- `yield`
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

### 3.1 Asignación

```cobra
x = 10
x = x + 5
```

### 3.2 Operadores aritméticos

- `+`, `-`, `*`, `/`, `%`, `**`

```cobra
resultado = (8 + 2) * 3
potencia = 2 ** 5
```

### 3.3 Operadores relacionales

- `==`, `!=`, `>`, `<`, `>=`, `<=`

### 3.4 Operadores lógicos

- `y`, `o`, `no`

```cobra
si edad >= 18 y activo:
    imprimir("Acceso permitido")
```

### 3.5 Interpolación y texto

```cobra
mensaje = f"Usuario: {nombre}, edad: {edad}"
imprimir(mensaje)
```

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
usar texto
usar numero
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

<!-- BEGIN: AUTO-CLI-TABLE -->
### Tabla CLI actualizada (autogenerado)

| Comando | Capacidad | Clase | Archivo |
|---|---|---|---|
| `agix` | `-` | `AgixCommand` | `src/pcobra/cobra/cli/commands/agix_cmd.py` |
| `bench` | `-` | `BenchCommand` | `src/pcobra/cobra/cli/commands/bench_cmd.py` |
| `benchmarks` | `-` | `BenchmarksCommand` | `src/pcobra/cobra/cli/commands/benchmarks_cmd.py` |
| `benchmarks2` | `-` | `BenchmarksV2Command` | `src/pcobra/cobra/cli/commands/benchmarks2_cmd.py` |
| `benchthreads` | `-` | `BenchThreadsCommand` | `src/pcobra/cobra/cli/commands/benchthreads_cmd.py` |
| `benchtranspilers` | `-` | `BenchTranspilersCommand` | `src/pcobra/cobra/cli/commands/bench_transpilers_cmd.py` |
| `build` | `codegen` | `BuildCommandV2` | `src/pcobra/cobra/cli/commands_v2/build_cmd.py` |
| `compilar` | `codegen` | `CompileCommand` | `src/pcobra/cobra/cli/commands/compile_cmd.py` |
| `contenedor` | `-` | `ContainerCommand` | `src/pcobra/cobra/cli/commands/container_cmd.py` |
| `crear` | `-` | `CrearCommand` | `src/pcobra/cobra/cli/commands/crear_cmd.py` |
| `dependencias` | `-` | `DependenciasCommand` | `src/pcobra/cobra/cli/commands/dependencias_cmd.py` |
| `docs` | `-` | `DocsCommand` | `src/pcobra/cobra/cli/commands/docs_cmd.py` |
| `ejecutar` | `execute` | `ExecuteCommand` | `src/pcobra/cobra/cli/commands/execute_cmd.py` |
| `empaquetar` | `-` | `EmpaquetarCommand` | `src/pcobra/cobra/cli/commands/empaquetar_cmd.py` |
| `gui` | `-` | `FletCommand` | `src/pcobra/cobra/cli/commands/flet_cmd.py` |
| `init` | `-` | `InitCommand` | `src/pcobra/cobra/cli/commands/init_cmd.py` |
| `interactive` | `-` | `InteractiveCommand` | `src/pcobra/cobra/cli/commands/interactive_cmd.py` |
| `jupyter` | `-` | `JupyterCommand` | `src/pcobra/cobra/cli/commands/jupyter_cmd.py` |
| `legacy` | `-` | `LegacyCommandGroupV2` | `src/pcobra/cobra/cli/commands_v2/legacy_cmd.py` |
| `mod` | `-` | `ModCommandV2` | `src/pcobra/cobra/cli/commands_v2/mod_cmd.py` |
| `modulos` | `-` | `ModulesCommand` | `src/pcobra/cobra/cli/commands/modules_cmd.py` |
| `paquete` | `-` | `PaqueteCommand` | `src/pcobra/cobra/cli/commands/package_cmd.py` |
| `qa-validar` | `codegen` | `QaValidarCommand` | `src/pcobra/cobra/cli/commands/qa_validar_cmd.py` |
| `qualia` | `-` | `QualiaCommand` | `src/pcobra/cobra/cli/commands/qualia_cmd.py` |
| `run` | `execute` | `RunCommandV2` | `src/pcobra/cobra/cli/commands_v2/run_cmd.py` |
| `test` | `codegen` | `TestCommandV2` | `src/pcobra/cobra/cli/commands_v2/test_cmd.py` |
| `validar-sintaxis` | `codegen` | `ValidarSintaxisCommand` | `src/pcobra/cobra/cli/commands/validar_sintaxis_cmd.py` |
| `verificar` | `codegen` | `VerifyCommand` | `src/pcobra/cobra/cli/commands/verify_cmd.py` |
<!-- END: AUTO-CLI-TABLE -->

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

Si vienes de comandos legacy como `cobra validar-sintaxis`, `cobra ejecutar` o
`cobra compilar`, migra al contrato público `run/build/test/mod` y revisa la
guía de transición en [`docs/migracion_cli_unificada.md`](migracion_cli_unificada.md).

---

## 11) Transpilación, targets y compatibilidad

El ecosistema maneja targets canónicos para distintos niveles de soporte.

### 11.1 Regla práctica

- Para máxima estabilidad operativa: usa targets Tier 1.
- Para experimentación/controlada: usa targets con soporte limitado o legacy según política vigente.

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

## 17) Roadmap de aprendizaje por niveles

### Nivel 1 — Fundamentos

- variables, tipos, condicionales, bucles,
- funciones simples,
- listas y diccionarios,
- ejecución local con CLI.

### Nivel 2 — Intermedio

- módulos e imports,
- manejo robusto de errores,
- diseño por capas,
- pruebas unitarias + integración.

### Nivel 3 — Avanzado

- asincronía y concurrencia,
- transpilación multi-target,
- optimización guiada por métricas,
- seguridad y sandbox en producción.

---

## 18) Apéndice: checklist de publicación de un proyecto Cobra

- [ ] `cobra run` sobre smoke tests de `src/`.
- [ ] tests pasando en CI.
- [ ] documentación de uso actualizada.
- [ ] ejemplos ejecutables y verificados.
- [ ] matriz de targets revisada para el release.

---

## Nota de consolidación documental

Este libro sustituye como guía de aprendizaje principal a documentos introductorios parciales o dispersos. Para especificación técnica detallada y política de targets, complementa con:

- `docs/SPEC_COBRA.md`
- `docs/especificacion_tecnica.md`
- `docs/targets_policy.md`
- `docs/MANUAL_COBRA.md`
