# Proyecto Cobra
[![Codecov](https://codecov.io/gh/Alphonsus411/pCobra/branch/work/graph/badge.svg)](https://codecov.io/gh/Alphonsus411/pCobra/branch/work)
[![Tier 1 PR Gate](https://github.com/Alphonsus411/pCobra/actions/workflows/test.yml/badge.svg?event=pull_request)](https://github.com/Alphonsus411/pCobra/actions/workflows/test.yml)
[![Tier 2 Nightly](https://github.com/Alphonsus411/pCobra/actions/workflows/test.yml/badge.svg?event=schedule)](https://github.com/Alphonsus411/pCobra/actions/workflows/test.yml)
[![Versión estable](https://img.shields.io/github/v/release/Alphonsus411/pCobra?label=stable)](https://github.com/Alphonsus411/pCobra/releases/latest)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Alphonsus411/pCobra/HEAD?labpath=notebooks/playground.ipynb)


## Qué es pCobra

Versión 10.0.13

- La caché incremental de AST y tokens se consolidó en **SQLitePlus** con script de migración y variables `SQLITE_DB_KEY`/`COBRA_DB_PATH` para definir la base de datos.
- `corelibs.asincrono` incorpora `grupo_tareas` y `reintentar_async`, reexportados en la biblioteca estándar para coordinar corrutinas y reintentos con *backoff*.
- `corelibs.texto`, `corelibs.numero` y `standard_library.datos` añaden validadores `es_*`, helpers como `prefijo_comun`/`sufijo_comun`, funciones `interpolar`/`envolver_modular` y lectura/escritura de Parquet y Feather.
- `corelibs.sistema.ejecutar` mantiene la ejecución en modo seguro con listas blancas obligatorias tanto en Python como en los *bindings* nativos.

[English version available here](docs/README.en.md)

pCobra es un lenguaje de programación escrito en español y pensado para la creación de herramientas, simulaciones y análisis en disciplinas como biología, computación y astrofísica. El proyecto integra un lexer, parser y un sistema de transpilación con una lista canónica de destinos de salida derivada automáticamente de `src/pcobra/cobra/config/transpile_targets.py` + `src/pcobra/cobra/transpilers/registry.py`.

Resumen normativo visible (generado desde la política canónica):

<!-- BEGIN GENERATED TARGET POLICY SUMMARY -->
- **Backends oficiales de salida**: 8 targets canónicos.
- **Targets oficiales de transpilación**: `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`.
- **Targets con runtime oficial verificable (full SDK solo en python)**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con verificación ejecutable explícita en CLI**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con runtime best-effort**: `go`, `java`.
- **Targets con soporte oficial mantenido de `corelibs`/`standard_library` (partial fuera de python)**: `python`, `rust`, `javascript`, `cpp`.
- **Targets con adaptador Holobit mantenido por el proyecto (partial fuera de python)**: `python`, `rust`, `javascript`, `cpp`.
- **Compatibilidad SDK completa (solo python)**: `python`.
- **Targets solo de transpilación**: `wasm`, `asm`.
- **Orígenes de transpilación inversa**: `python`, `javascript`, `java`. Este alcance reverse de entrada está separado de los 8 targets oficiales de salida.

Tiers oficiales de soporte de backends:

- **Tier 1**: `python`, `rust`, `javascript`, `wasm`.
- **Tier 2**: `go`, `cpp`, `java`, `asm`.
<!-- END GENERATED TARGET POLICY SUMMARY -->

Fuentes normativas: `src/pcobra/cobra/config/transpile_targets.py` para la lista canónica y los tiers, y `src/pcobra/cobra/cli/target_policies.py` para la separación entre transpilación, runtime oficial y verificación ejecutable.

### Política de targets oficial

La política oficial de targets exige que toda documentación pública, snippets de CLI, tablas y ejemplos utilicen exclusivamente los nombres canónicos `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java` y `asm`. Los tiers oficiales se derivan de `TIER1_TARGETS`, `TIER2_TARGETS` y `OFFICIAL_TARGETS` definidos en `src/pcobra/cobra/config/transpile_targets.py`, con el registro canónico de backends en `src/pcobra/cobra/transpilers/registry.py`.

Además, el proyecto separa explícitamente **targets oficiales de salida** de **targets con runtime oficial de ejecución**. Hoy la ejecución oficial verificable —en sandbox, contenedor o comando de verificación— cubre `python`, `javascript`, `cpp` y `rust`, tal y como reflejan `src/pcobra/cobra/cli/target_policies.py`, `src/pcobra/core/sandbox.py`, `src/pcobra/cobra/cli/commands/verify_cmd.py` y el objetivo `make docker`. En la misma categoría quedan el soporte oficial mantenido de `corelibs`/`standard_library` y el soporte Holobit mantenido por el proyecto en esos runtimes. Los targets `go` y `java` se conservan como **runtime best-effort**, mientras que `wasm` y `asm` son **targets solo de transpilación**. Ninguna de esas categorías debe interpretarse como runtime Docker/sandbox oficial equivalente, ni como soporte oficial de librerías en ejecución comparable al de `python`, `rust`, `javascript` o `cpp`.

La compatibilidad mínima por backend no es uniforme: `src/pcobra/cobra/transpilers/compatibility_matrix.py` declara `python` como `full` para la matriz contractual actual, mientras `javascript`, `rust`, `wasm`, `go`, `cpp`, `java` y `asm` se mantienen en `partial`. Eso significa que la **paridad SDK total** solo puede prometerse para `python`. `javascript`, `rust` y `cpp` sí cuentan con runtime oficial verificable y adaptadores mantenidos por el proyecto, pero siguen siendo `partial` en Holobit/SDK. `go` y `java` se mantienen como runtimes best-effort; `wasm` y `asm` como salidas oficiales solo de transpilación. Ninguna de esas categorías debe venderse como runtime oficial verificable ni como compatibilidad SDK equivalente.

### Política de soporte por tiers (SLA y gobernanza)

Definición operativa oficial:

- **Tier 1** (`python`, `rust`, `javascript`, `wasm`): prioridad alta de corrección para regresiones de transpilación y coherencia documental.
- **Tier 2** (`go`, `cpp`, `java`, `asm`): soporte contractual mantenido con prioridad secundaria frente a Tier 1.

SLA de mantenimiento documental/técnico:

- **Tier 1**: incidencias de regresión de transpilación o desalineación de política deben tener triage inicial en **<= 2 días hábiles** y propuesta de remediación en la siguiente ventana activa de mantenimiento.
- **Tier 2**: incidencias equivalentes deben tener triage inicial en **<= 5 días hábiles** y corrección según planificación de release o ventana de mantenimiento no crítica.

Criterios de **promoción** de Tier 2 → Tier 1 (todos requeridos durante al menos dos releases consecutivas):

1. Señal estable de uso real.
2. Cobertura CI sostenida en PR y/o gates equivalentes de calidad.
3. Runtime/documentación sin desviaciones contractuales frente a la matriz pública.

Criterios de **degradación** de Tier 1 → Tier 2:

1. Incumplimiento sostenido de cobertura CI o calidad operativa.
2. Dependencias externas no mantenibles en la ventana de releases.
3. Brecha contractual repetida entre documentación, CLI y comportamiento real.

Cualquier cambio de tier requiere RFC, plan de migración y comunicación explícita en changelog/notas de release.

### Prerrequisitos por backend de ejecución/runtime

Además del estado `full/partial`, cada backend depende de toolchains o runtime externos que deben existir en el host:

- `python` (`full`): entorno Python `>=3.10` con dependencias del proyecto; `holobit_sdk` es obligatorio para el contrato Holobit completo.
- `javascript` (`partial`): `node` y dependencias del runtime JavaScript del proyecto (`vm2`/`node-fetch` cuando aplique en el host).
- `rust` (`partial`): toolchain Rust (`rustc`/`cargo`) para compilación/ejecución fuera de transpilación.
- `cpp` (`partial`): compilador `cpp` (`gpp`/`clangpp`) y toolchain nativa del sistema.
- `go` (`partial`, best-effort): toolchain Go instalada en el host.
- `java` (`partial`, best-effort): JDK/JRE en el host.
- `wasm` (`partial`, solo transpilación): host WASM con imports `pcobra:*` para `corelibs`, `standard_library` y Holobit; el módulo generado no embebe ese runtime.
- `asm` (`partial`, solo transpilación): runtime/ensamblador externo administrado fuera de pCobra.

Sin estos prerrequisitos, pCobra puede conservar generación de código, pero no promete ejecución equivalente al runtime oficial de Python.

**Nota explícita de política:** **los backends retirados no forman parte del árbol operativo**.

Guía de migración para consumidores de targets retirados: `docs/migracion_targets_retirados.md`.

### Compatibilidad explícita por target (Holobit SDK + librerías)

| Target | Tier | Holobit SDK | `holobit`/`proyectar`/`transformar`/`graficar` | `corelibs` | `standard_library` |
|---|---|---|---|---|---|
| `python` | Tier 1 | ✅ `full` (requiere `holobit-sdk`) | ✅ `full` | ✅ `full` | ✅ `full` |
| `rust` | Tier 1 | 🟡 `partial` (sin dependencia de SDK Python) | 🟡 `partial` | 🟡 `partial` | 🟡 `partial` |
| `javascript` | Tier 1 | 🟡 `partial` (sin dependencia de SDK Python) | 🟡 `partial` | 🟡 `partial` | 🟡 `partial` |
| `wasm` | Tier 1 | 🟡 `partial` vía host (`pcobra:*`) | 🟡 `partial` | 🟡 `partial` | 🟡 `partial` |
| `go` | Tier 2 | 🟡 `partial` best-effort | 🟡 `partial` | 🟡 `partial` | 🟡 `partial` |
| `cpp` | Tier 2 | 🟡 `partial` con adaptador mantenido | 🟡 `partial` | 🟡 `partial` | 🟡 `partial` |
| `java` | Tier 2 | 🟡 `partial` best-effort | 🟡 `partial` | 🟡 `partial` | 🟡 `partial` |
| `asm` | Tier 2 | 🟡 `partial` de inspección/diagnóstico | 🟡 `partial` | 🟡 `partial` | 🟡 `partial` |

Fuente normativa de detalle: `docs/contrato_runtime_holobit.md` y `docs/matriz_transpiladores.md`.

El objetivo de pCobra es brindar a la comunidad hispanohablante una alternativa cercana para aprender y construir software, reduciendo la barrera del idioma y fomentando la colaboración abierta. A medida que evoluciona, el proyecto busca ampliar su ecosistema, mejorar la transpilación y proveer herramientas que sirvan de puente entre la educación y el desarrollo profesional.


## Tabla de Contenidos

- Descripción del Proyecto
- Arquitectura del compilador
- Instalación
- Cómo usar la CLI
- Descargas
- Estructura del Proyecto
- Herramientas y scripts soportados
- Características Principales
- Uso
- Tokens y reglas léxicas
- Ejemplo de Uso
- Conversión desde otros lenguajes
- Pruebas
- Ejemplos de prueba
- Generar documentación
- Análisis con CodeQL
- [CobraHub](docs/frontend/cobrahub.rst)
- Hitos y Roadmap
- Contribuciones
- [Guía de Contribución](CONTRIBUTING.md)
- [Proponer extensiones](docs/frontend/rfc_plugins.rst)
- Extensión para VS Code
- [Comunidad](docs/comunidad.md)
- Licencia
- [Manual de Cobra](docs/MANUAL_COBRA.md)
- [Manual de Cobra en formato reStructuredText](docs/MANUAL_COBRA.rst)
- [Manual de Cobra en PDF](https://alphonsus411.github.io/pCobra/proyectocobra.pdf)
- [Guía básica](docs/guia_basica.md)
- [Especificación técnica](docs/especificacion_tecnica.md)
- [Blog del minilenguaje](docs/blog_minilenguaje.md)
- [Casos de uso reales](docs/casos_reales.md)
- [Limitaciones del sandbox de Node](docs/limitaciones_node_sandbox.md)
- [Limitaciones del sandbox de `cpp`](docs/limitaciones_cpp_sandbox.md)
- Notebooks de ejemplo y casos reales
- Probar Cobra en línea
- [Historial de cambios](CHANGELOG.md)

## Ejemplos

Proyectos de demostración disponibles en el [repositorio de ejemplos](https://github.com/Alphonsus411/pCobra/tree/HEAD/examples).
Este repositorio incluye ejemplos básicos en la carpeta `examples/`, por
ejemplo `examples/funciones_principales.co` que muestra condicionales, bucles y
definición de funciones en Cobra.
Para ejemplos interactivos revisa los cuadernos en `notebooks/casos_reales/`.

### Ejemplos avanzados

En [examples/avanzados/](examples/avanzados/) se incluyen programas que profundizan
en Cobra con ejercicios de control de flujo, funciones recursivas e interacción
de clases. Cada tema cuenta con su propia carpeta:

- [examples/avanzados/control_flujo/](examples/avanzados/control_flujo/)
- [examples/avanzados/funciones/](examples/avanzados/funciones/)
- [examples/avanzados/clases/](examples/avanzados/clases/)

## Notebooks de ejemplo

En la carpeta `notebooks/` se incluye el cuaderno `ejemplo_basico.ipynb` con un ejemplo básico de uso de Cobra. Además, los cuadernos de `notebooks/casos_reales/` muestran cómo ejecutar los ejemplos avanzados. Para abrirlo ejecuta:

```bash
cobra jupyter --notebook notebooks/ejemplo_basico.ipynb
```
Si omites el argumento ``--notebook`` se abrirá Jupyter Notebook de manera convencional y podrás escoger el archivo desde la interfaz web.



## Probar Cobra en línea

Puedes experimentar con Cobra directamente en tu navegador:

- [Replit](https://replit.com/github/Alphonsus411/pCobra)
- [Binder](https://mybinder.org/v2/gh/Alphonsus411/pCobra/HEAD?labpath=notebooks/playground.ipynb)
- [GitHub Codespaces](https://codespaces.new/Alphonsus411/pCobra)

## Descripción del Proyecto

Cobra está diseñado para facilitar la programación en español, permitiendo que los desarrolladores utilicen un lenguaje más accesible. A través de su lexer, parser y transpiladores, Cobra puede analizar, ejecutar y convertir código a otros lenguajes, brindando soporte para variables, funciones, estructuras de control y estructuras de datos como listas, diccionarios y clases.
Para un tutorial paso a paso consulta el [Manual de Cobra](docs/MANUAL_COBRA.rst).
La especificación completa del lenguaje se encuentra en [SPEC_COBRA.md](docs/SPEC_COBRA.md).

## Arquitectura del compilador

La cadena de herramientas de Cobra separa el front-end de los generadores de código mediante una arquitectura interna de compilación. Esa arquitectura es un detalle de implementación y no forma parte de la lista pública de backends oficiales. El flujo principal funciona de la siguiente manera:

1. El front-end analiza el código fuente y construye el AST de Cobra.
2. Ese AST se normaliza internamente para coordinar estructuras de control, módulos y tipos antes de la generación de código.
3. Los transpiladores consumen esa IR para generar código en los distintos backends soportados.

Esta organización actúa como contrato técnico entre el front-end y los generadores de código, permitiendo incorporar mejoras internas sin modificar el parser original. Gracias a ello, Cobra ofrece un generador para el target canónico `asm` que produce instrucciones simbólicas optimizadas para depuración y diagnóstico de rendimiento. En la documentación pública, la salida oficial sigue limitada a `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java` y `asm`.

## Instalación

```bash
pip install pcobra
```

### Instalación por perfiles (extras opcionales)

```bash
# Excel (.xlsx)
pip install "pcobra[excel]"

# Formatos columnares/binarios (Parquet/Feather)
pip install "pcobra[columnar]"
# alias equivalente
pip install "pcobra[io-binary]"

# Servidor de lenguaje (LSP)
pip install "pcobra[lsp]"

# Generación de documentación
pip install "pcobra[docs]"
```

Si instalas desde el repositorio local, usa la misma sintaxis con `.`:

```bash
pip install -e .[excel]
```

### Instalación con pipx

```bash
pipx install pcobra
```

### Instalación desde repositorio

Consulta [docs/instalacion.md](docs/instalacion.md#instalacion-desde-repositorio) para instrucciones avanzadas (gramáticas, plugins, scripts y uso de Docker).

### Bootstrap opcional de `PATH` para desarrollo local

Desde esta versión, `import pcobra` **ya no modifica** `PATH` automáticamente. Si necesitas que la CLI añada `scripts/bin` al `PATH` al iniciar (flujos locales del repositorio), actívalo explícitamente:

```bash
PCOBRA_CLI_BOOTSTRAP_PATH=1 cobra --help
```

Este comportamiento solo aplica al arranque de la CLI (`pcobra/cli.py`) y mantiene las importaciones de librería libres de efectos secundarios.

## Cómo usar la CLI

Ejecuta un archivo de Cobra con:

```bash
cobra archivo.co
```

Para listar las opciones disponibles ejecuta:

```bash
cobra --help
```

El intérprete se ejecuta en modo seguro por defecto. Si deseas desactivarlo utiliza la opción `--no-seguro`:

```bash
cobra archivo.co --no-seguro
```

### Ejemplo de transpilación

```bash
cobra compilar hola.co --backend python
```

Esto generará `hola.py`. Para conocer otros destinos y opciones, consulta la [documentación detallada](docs/) o revisa [docs/frontend](docs/frontend).

## Descarga de binarios

Para cada lanzamiento se generan ejecutables para Linux, Windows y macOS mediante
GitHub Actions. Puedes encontrarlos en la pestaña
[Releases](https://github.com/Alphonsus411/pCobra/releases) del repositorio.
Solo descarga el archivo correspondiente a tu sistema operativo desde la versión
más reciente y ejecútalo directamente.

Crear un tag `vX.Y.Z` en GitHub desencadena la publicación automática del
paquete en PyPI y la actualización de la imagen Docker.

Si prefieres generar el ejecutable manualmente ejecuta desde la raíz del
repositorio en tu sistema (Windows, macOS o Linux):

```bash
pip install pyinstaller
cobra empaquetar --output dist
```
El nombre del binario puede ajustarse con la opción `--name`. También puedes
usar un archivo `.spec` propio o agregar datos adicionales mediante
``--spec`` y ``--add-data``:

```bash
cobra empaquetar --spec build/cobra.spec \
  --add-data "all-bytes.dat;all-bytes.dat" --output dist
```

## Crear un ejecutable con PyInstaller

Para compilar Cobra de forma independiente primero crea y activa un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows usa .\\.venv\\Scripts\\activate
```

Instala la distribución publicada y PyInstaller:

```bash
pip install pcobra
pip install pyinstaller
```

Luego genera el binario con:

```bash
pyinstaller --onefile src/pcobra/cli/cli.py -n cobra
```

El ejecutable aparecerá en el directorio `dist/`.

Para realizar una prueba rápida puedes ejecutar el script
`scripts/test_pyinstaller.sh`. Este script crea un entorno virtual temporal,
instala `pcobra` desde el repositorio (o desde PyPI si se ejecuta fuera
de él) y ejecuta PyInstaller sobre `src/pcobra/cli/cli.py` o el script `cobra-init`.
El binario resultante se
guardará por defecto en `dist/`.

```bash
scripts/test_pyinstaller.sh
```


## Descargas

Los ejecutables precompilados para Cobra se publican en la sección de [Releases](https://github.com/Alphonsus411/pCobra/releases).

| Versión | Plataforma | Enlace |
| --- | --- | --- |
| 10.0.12 | Linux x86_64 | [cobra-linux](https://github.com/Alphonsus411/pCobra/releases/download/v10.0.12/cobra-linux) |
| 10.0.12 | Windows x86_64 | [cobra.exe](https://github.com/Alphonsus411/pCobra/releases/download/v10.0.12/cobra.exe) |
| 10.0.12 | macOS arm64 | [cobra-macos](https://github.com/Alphonsus411/pCobra/releases/download/v10.0.12/cobra-macos) |

Para comprobar la integridad del archivo descargado calcula su hash SHA256 y compáralo con el publicado:

```bash
sha256sum cobra-linux
```

En Windows utiliza:

```powershell
CertUtil -hashfile cobra.exe SHA256
```

# Estructura del Proyecto

El proyecto se organiza en las siguientes carpetas:

- `src/pcobra/`: Código fuente del paquete.
- `docs/`: Documentación del proyecto.
- `tests/`: Pruebas automáticas.
- `examples/`: Ejemplos de uso.
- `extensions/`: Extensiones oficiales, como la de VS Code.
- `scripts/`: Scripts de utilidad.
- `notebooks/`: Cuadernos interactivos.
- `docker/`: Archivos de configuración para contenedores.
- `binder/`: Archivos para ejecutar el proyecto en Binder.

Los archivos `requirements*.txt` son *locks* generados automáticamente a partir de `pyproject.toml`, que es la única fuente de verdad para dependencias de runtime y extras (`dev`, `docs`, `notebooks`, etc.).

Para regenerarlos de forma reproducible usa:

```bash
make deps-sync
# o con actualización de versiones compatibles
bash scripts/sync_requirements.sh --upgrade
```

Para validar que no hay drift entre `pyproject.toml` y los locks:

```bash
make deps-check
```

# Herramientas y scripts soportados

El proyecto soporta oficialmente:

- `Makefile` para automatizar tareas como `make install`, `make test` y `make clean`.
- `scripts/run.sh` para ejecutar Cobra con variables definidas en `.env`.
- `scripts/install.sh` para preparar el entorno de desarrollo.
- Scripts auxiliares en `scripts/`.
- Configuraciones Docker en `docker/`.

# Características Principales

- Lexer y Parser: Implementación de un lexer para la tokenización del código fuente y un parser para la construcción de un árbol de sintaxis abstracta (AST).
- Transpiladores a Python, JavaScript, `asm`, Rust, `cpp`, Go, Java y WebAssembly: Cobra puede convertir el código en estos targets oficiales, facilitando su integración con aplicaciones externas.
- Soporte de Estructuras Avanzadas: Permite la declaración de variables, funciones, clases, listas y diccionarios, así como el uso de bucles y condicionales.
- Módulos nativos con funciones de E/S, utilidades matemáticas y estructuras de datos para usar directamente desde Cobra.
- Instalación de paquetes en tiempo de ejecución mediante la instrucción `usar`.
- Manejo de Errores: El sistema captura y reporta errores de sintaxis, facilitando la depuración.
- Visualización y Depuración: Salida detallada de tokens, AST y errores de sintaxis para un desarrollo más sencillo.
- Decoradores de rendimiento: la biblioteca ``smooth-criminal`` ofrece
  funciones como ``optimizar`` y ``perfilar`` para mejorar y medir la
  ejecución de código Python desde Cobra.
- Benchmarking: ejemplos completos de medición de rendimiento están
  disponibles en `docs/frontend/benchmarking.rst`.
- Ejemplos de Código y Documentación: Ejemplos prácticos que ilustran el uso del lexer, parser y transpiladores.
- Ejemplos Avanzados: Revisa `docs/frontend/ejemplos_avanzados.rst` para conocer casos con clases, hilos y manejo de errores.
- Identificadores en Unicode: Puedes nombrar variables y funciones utilizando
  caracteres como `á`, `ñ` o `Ω` para una mayor flexibilidad.

## Rendimiento

Los benchmarks más recientes se ejecutaron con
`scripts/benchmarks/compare_backends.py` para comparar varios backends. El
tiempo aproximado fue de **0.68&nbsp;s** para Cobra y Python,
**0.07&nbsp;s** para JavaScript y **0.04&nbsp;s** para Rust, sin consumo
significativo de memoria.

Ejecuta el script con:

```bash
python scripts/benchmarks/compare_backends.py --output bench_results.json
```

El archivo [bench_results.json](bench_results.json) se guarda en el directorio
actual y puede analizarse con el cuaderno
[notebooks/benchmarks_resultados.ipynb](notebooks/benchmarks_resultados.ipynb).

Para ver la evolución entre versiones ejecuta:

```bash
python scripts/benchmarks/compare_releases.py --output benchmarks_compare.json
```

Los resultados históricos se publican como archivos `benchmarks.json` en la
[sección de Releases](https://github.com/Alphonsus411/pCobra/releases), donde
puedes consultar las métricas de cada versión.

Para comparar el rendimiento de los hilos ejecuta `cobra benchthreads`:

```bash
cobra benchthreads --output threads.json
```

El resultado contiene tres entradas (secuencial, cli_hilos y kernel_hilos) con
los tiempos y uso de CPU.

Para generar binarios en `cpp` y Rust y medir su rendimiento ejecuta:

```bash
cobra bench --binary
```

Los resultados se guardan en `binary_bench.json`.

# Uso

Para ejecutar el proyecto directamente desde el repositorio se incluye el
script `scripts/run.sh`. Este cargará las variables definidas en `.env` si dicho archivo
existe y luego llamará a `python -m pcobra` pasando todos los argumentos
recibidos. Úsalo de la siguiente forma:

```bash
./scripts/run.sh [opciones]
```

También puedes ejecutar la interfaz de línea de comandos directamente desde la
raíz del proyecto:

```bash
python -m pcobra
```

Entrypoints oficiales de CLI:

- `pcobra.cli:main` (script `cobra` instalado por packaging).
- `python -m pcobra` (passthrough directo a `pcobra.cli:main`).

Rutas soportadas explícitamente para compatibilidad de arranque/import:

- `pcobra.cli` ✅ ruta canónica.
- `cobra.cli.cli` ✅ shim legacy soportado.
- `python -m pcobra` ✅ ejecuta la ruta canónica.
- `python -m cobra.cli.cli` ✅ ejecuta el shim legacy canónico.

El módulo `src/pcobra/core/main.py` se conserva como ejemplo/demo interno y no
debe usarse como entrypoint productivo.

Para conocer las opciones avanzadas del modo seguro revisa
`docs/frontend/modo_seguro.rst`. Los ejemplos de medición de rendimiento
están disponibles en `docs/frontend/benchmarking.rst`.

Para ejecutar pruebas unitarias, utiliza pytest:

````bash
PYTHONPATH=$PWD pytest tests --cov=pcobra --cov-report=term-missing \
  --cov-fail-under=95
````

También puedes ejecutar suites específicas ubicadas en `tests`:

````bash
python -m tests.suite_cli           # Solo pruebas de la CLI
python -m tests.suite_core          # Pruebas de lexer, parser e intérprete
python -m tests.suite_transpiladores  # Pruebas de los transpiladores
````

## Uso directo desde el repositorio

El archivo `sitecustomize.py` se carga automáticamente cuando Python se
ejecuta desde la raíz del proyecto. Este módulo añade la carpeta `src` a
`sys.path`, permitiendo importar paquetes como `src.modulo` sin instalar
el paquete ni modificar `PYTHONPATH`.

Para probar Cobra de esta forma realiza lo siguiente:

```bash
python -m venv .venv
source .venv/bin/activate  # En Unix
.\.venv\Scripts\activate  # En Windows
make run                   # o bien: python -m pcobra
```

## Tokens y reglas léxicas

El analizador léxico convierte el código en tokens de acuerdo con las
expresiones regulares definidas en `lexer.py`. En la siguiente tabla se
describen todos los tokens disponibles:

| Token | Descripción |
|-------|-------------|
| DIVIDIR | Palabra clave o instrucción "dividir" |
| MULTIPLICAR | Palabra clave o instrucción "multiplicar" |
| CLASE | Palabra clave "clase" |
| DICCIONARIO | Palabra clave "diccionario" |
| LISTA | Palabra clave "lista" |
| RBRACE | Símbolo "}" |
| DEF | Palabra clave "def" |
| IN | Palabra clave "in" |
| LBRACE | Símbolo "{" |
| FOR | Palabra clave "for" |
| DOSPUNTOS | Símbolo ":" |
| VAR | Palabra clave "var" |
| FUNC | Palabra clave "func" o "definir" |
| SI | Palabra clave "si" |
| SINO | Palabra clave "sino" |
| MIENTRAS | Palabra clave "mientras" |
| PARA | Palabra clave "para" |
| IMPORT | Palabra clave "import" |
| USAR | Palabra clave "usar" |
| MACRO | Palabra clave "macro" |
| HOLOBIT | Palabra clave "holobit" |
| PROYECTAR | Palabra clave "proyectar" |
| TRANSFORMAR | Palabra clave "transformar" |
| GRAFICAR | Palabra clave "graficar" |
| TRY | Palabra clave "try" o "intentar" |
| CATCH | Palabra clave "catch" o "capturar" |
| THROW | Palabra clave "throw" o "lanzar" |
| ENTERO | Número entero |
| FLOTANTE | Número con punto decimal |
| CADENA | Cadena de caracteres |
| BOOLEANO | Literal booleano |
| IDENTIFICADOR | Nombre de variable o función |
| ASIGNAR | Símbolo "=" |
| SUMA | Operador "+" |
| RESTA | Operador "-" |
| MULT | Operador "*" |
| DIV | Operador "/" |
| MAYORQUE | Operador ">" |
| MENORQUE | Operador "<" |
| MAYORIGUAL | Operador ">=" |
| MENORIGUAL | Operador "<=" |
| IGUAL | Operador "==" |
| DIFERENTE | Operador "!=" |
| AND | Operador lógico "&&" |
| OR | Operador lógico "||" |
| NOT | Operador "!" |
| MOD | Operador "%" |
| LPAREN | Símbolo "(" |
| RPAREN | Símbolo ")" |
| LBRACKET | Símbolo "[" |
| RBRACKET | Símbolo "]" |
| COMA | Símbolo "," |
| RETORNO | Palabra clave "retorno" |
| FIN | Palabra clave "fin" |
| EOF | Fin de archivo |
| IMPRIMIR | Palabra clave "imprimir" |
| HILO | Palabra clave "hilo" |
| ASINCRONICO | Palabra clave "asincronico" |
| DECORADOR | Símbolo "@" |
| YIELD | Palabra clave "yield" |
| ESPERAR | Palabra clave "esperar" |
| ROMPER | Palabra clave "romper" |
| CONTINUAR | Palabra clave "continuar" |
| PASAR | Palabra clave "pasar" |
| AFIRMAR | Palabra clave "afirmar" |
| ELIMINAR | Palabra clave "eliminar" |
| GLOBAL | Palabra clave "global" |
| NOLOCAL | Palabra clave "nolocal" |
| LAMBDA | Palabra clave "lambda" |
| CON | Palabra clave "con" |
| FINALMENTE | Palabra clave "finalmente" |
| DESDE | Palabra clave "desde" |
| COMO | Palabra clave "como" |
| SWITCH | Palabra clave "switch" o "segun" |
| CASE | Palabra clave "case" o "caso" |

Las expresiones regulares se agrupan en `especificacion_tokens` y se procesan en orden para encontrar coincidencias. Las palabras clave usan patrones como `\bvar\b` o `\bfunc\b`, los números emplean `\d+` o `\d+\.\d+` y las cadenas se detectan con `"[^\"]*"` o `'[^']*'`. Los identificadores permiten caracteres Unicode mediante `[^\W\d_][\w]*`. Operadores y símbolos utilizan patrones directos como `==`, `&&` o `\(`. Antes del análisis se eliminan los comentarios de línea y de bloque con `re.sub`.

# Ejemplo de Uso

Puedes probar el lexer y parser con un código como el siguiente:

```python
from cobra.core import Lexer, Parser
from cobra.transpilers.transpiler.to_python import TranspiladorPython

codigo = """
var x = 10
si x > 5 :
    proyectar(x, "2D")
sino :
    graficar(x)
"""

lexer = Lexer(codigo)
tokens = lexer.analizar_token()

parser = Parser(tokens)

arbol = parser.parsear()
print(arbol)

transpiler = TranspiladorPython()
codigo_python = transpiler.generate_code(arbol)
print(codigo_python)
```

## Ejemplo de imprimir, holobits y bucles

A continuación se muestra un fragmento que utiliza `imprimir`, holobits y bucles:

````cobra
codigo = '''
var h = holobit([0.8, -0.5, 1.2])
imprimir(h)

var contador = 0
mientras contador < 3 :
    imprimir(contador)
    contador += 1

para var i en rango(2) :
    imprimir(i)
'''
````

Al generar código para Python, `imprimir` se convierte en `print`, `mientras` en `while` y `para` en `for`. En JavaScript estos elementos se transforman en `console.log`, `while` y `for...of` respectivamente. Para el target `asm` se generan instrucciones `PRINT`, `WHILE` y `FOR`. En Rust se produce código equivalente con `println!`, `while` y `for`. En `cpp` se obtienen construcciones con `std::cout`, `while` y `for`. El tipo `holobit` se traduce a la llamada `holobit([...])` en Python, `new Holobit([...])` en JavaScript, `holobit(vec![...])` en Rust o `holobit({ ... })` en `cpp`. En Go se genera `fmt.Println` y en Java se usa `System.out.println`.

## Integración con holobit-sdk

El proyecto declara `holobit-sdk==1.0.8` en `pyproject.toml` como dependencia **obligatoria** cuando se instala con Python `>=3.10`. Las funciones `graficar`, `proyectar`, `transformar`, `escalar` y `mover` del runtime Python delegan en esa API para ese entorno. Dentro de ese grupo, `escalar` y `mover` son helpers **solo Python** y no forman parte del contrato Holobit multi-backend documentado en `docs/contrato_runtime_holobit.md` y `docs/matriz_transpiladores.md`. Si el entorno queda desalineado y `holobit_sdk` falta igualmente, el runtime prioriza **errores explícitos** en lugar de prometer emulación completa en todos los entornos.

```python
from core.holobits import Holobit, graficar, proyectar, transformar, escalar, mover

h = Holobit([0.8, -0.5, 1.2, 0.0, 0.0, 0.0])
proyectar(h, "2D")
graficar(h)
transformar(h, "rotar", "z", 90)
escalar(h, 2.0)
mover(h, 1.0, 0.0, -1.0)
```

## Ejemplo de carga de módulos

Puedes dividir el código en varios archivos y cargarlos con `import`:

````cobra
# modulo.co
var saludo = 'Hola desde módulo'

# programa.co
import 'modulo.co'
imprimir(saludo)
````

Al ejecutar `programa.co`, se procesará primero `modulo.co` y luego se imprimirá `Hola desde módulo`.

## Instrucción `usar` para dependencias dinámicas

La sentencia `usar "paquete"` intenta importar un módulo de Python. Si el
paquete no está disponible, Cobra ejecutará `pip install paquete` para
instalarlo y luego lo cargará en tiempo de ejecución. Cuando la entrada de la
lista blanca incluye hashes (`--hash=`) se añade automáticamente la bandera
`--require-hashes` para que `pip` verifique el contenido; de lo contrario se
omite. El módulo queda registrado en el entorno bajo el mismo nombre para su
uso posterior.
Para restringir qué dependencias pueden instalarse se emplea la variable
`USAR_WHITELIST` definida en `src/pcobra/cobra/usar_loader.py`. Basta con
añadir o quitar nombres de paquetes en dicho conjunto para modificar la lista
autorizada. Si la lista se deja vacía la función `obtener_modulo` lanzará
`PermissionError`, por lo que es necesario poblarla antes de permitir
instalaciones dinámicas.

Para habilitar la instalación automática define la variable de entorno
`COBRA_USAR_INSTALL=1`. Cuando esta variable no esté establecida,
`obtener_modulo()` rechazará instalar dependencias y lanzará un
`RuntimeError` si el paquete no se encuentra.

## Archivo de mapeo de módulos

Los transpiladores consultan `cobra.mod` para resolver las importaciones.
Este archivo sigue un esquema YAML sencillo donde cada clave es la ruta del
módulo Cobra y sus valores indican las rutas de los archivos generados.

Ejemplo de formato:

```yaml
modulo.co:
  version: "1.0.0"
  python: modulo.py
  javascript: modulo.js
```

Si una entrada no se encuentra, el transpilador cargará directamente el archivo
indicado en la instrucción `import`. Para añadir o modificar rutas basta con
editar `cobra.mod` y volver a ejecutar las pruebas.

## Invocar el transpilador

La carpeta [`src/pcobra/cobra/transpilers/transpiler`](src/pcobra/cobra/transpilers/transpiler)
contiene la implementación de los transpiladores a Python, JavaScript, `asm`, Rust, `cpp`, Go, Java y WebAssembly. Una vez
instaladas las dependencias, puedes llamar al transpilador desde tu propio
script de la siguiente manera:

```python
from cobra.transpilers.transpiler.to_python import TranspiladorPython
from cobra.core import Parser

codigo = "imprimir('hola')"
parser = Parser(codigo)
arbol = parser.parsear()
transpiler = TranspiladorPython()
resultado = transpiler.generate_code(arbol)
print(resultado)
```

Para otros lenguajes puedes invocar los nuevos transpiladores así:

```python
from cobra.transpilers.transpiler.to_js import TranspiladorJavaScript
from cobra.transpilers.transpiler.to_rust import TranspiladorRust
from cobra.transpilers.transpiler.to_cpp import TranspiladorCPP
from cobra.transpilers.transpiler.to_go import TranspiladorGo
from cobra.transpilers.transpiler.to_java import TranspiladorJava
from cobra.transpilers.transpiler.to_asm import TranspiladorASM
from cobra.transpilers.transpiler.to_wasm import TranspiladorWasm

codigo_js = TranspiladorJavaScript().generate_code(arbol)
codigo_rust = TranspiladorRust().generate_code(arbol)
codigo_cpp = TranspiladorCPP().generate_code(arbol)
codigo_go = TranspiladorGo().generate_code(arbol)
codigo_java = TranspiladorJava().generate_code(arbol)
codigo_asm = TranspiladorASM().generate_code(arbol)
codigo_wasm = TranspiladorWasm().generate_code(arbol)
```

Tras obtener el código con ``generate_code`` puedes guardarlo usando ``save_file``:

```python
transpiler.save_file("salida.py")
```

Requiere tener instalado el paquete en modo editable y todas las dependencias
de `requirements.txt`. Si necesitas generar archivos a partir de módulos Cobra,
consulta el mapeo definido en `cobra.mod`.

## Ejemplo de concurrencia

Es posible lanzar funciones en hilos con la palabra clave `hilo`:

````cobra
func tarea():
    imprimir('trabajo')
fin

hilo tarea()
imprimir('principal')
````

Al generar código para estas funciones, se crean llamadas `asyncio.create_task` en Python y `Promise.resolve().then` en JavaScript.

## Uso desde la CLI

Una vez instalado el paquete, la herramienta `cobra` ofrece varios subcomandos:

### Autocompletado

La CLI soporta autocompletado de argumentos mediante
[argcomplete](https://kislyuk.github.io/argcomplete/). Para habilitarlo en tu
terminal ejecuta uno de los siguientes comandos según tu *shell*:

- **bash**:

  ```bash
  eval "$(register-python-argcomplete cobra)"
  ```

- **zsh**:

  ```bash
  autoload -U bashcompinit
  bashcompinit
  eval "$(register-python-argcomplete cobra)"
  ```

- **fish**:

  ```bash
  register-python-argcomplete --shell fish cobra | source
  ```

```bash
# Compilar un archivo a: python, rust, javascript, wasm, go, cpp, java o asm
cobra compilar programa.co --backend python

# Transpilar inverso de Python a JavaScript
cobra transpilar-inverso script.py --origen=python --destino=javascript

# Ejemplo de mensaje de error al compilar un archivo inexistente
cobra compilar noexiste.co
# Salida:
# Error: El archivo 'noexiste.co' no existe


# Gestionar módulos instalados
cobra modulos listar
cobra modulos instalar ruta/al/modulo.co
cobra modulos remover modulo.co
# Crear e instalar paquetes Cobra
cobra paquete crear src demo.cobra
cobra paquete instalar demo.cobra
# Generar documentación HTML y API
cobra docs
# Crear un ejecutable independiente
cobra empaquetar --output dist
# Perfilar un programa y guardar los resultados
cobra profile programa.co --output salida.prof
# O mostrar el perfil directamente en pantalla
cobra profile programa.co
# Compilar en varios backends en una sola llamada
cobra compilar ejemplo.co --tipos=python,javascript
# Iniciar el iddle gráfico (requiere Flet)
cobra gui
```

Si deseas desactivar los colores usa `--no-color`:

```bash
cobra --no-color ejecutar programa.co
```

Para aumentar el nivel de detalle de los mensajes añade `-v` o `--verbose`.
Por defecto el nivel de registro es `INFO`; con `-v` o más se cambia a `DEBUG`:

```bash
cobra -v ejecutar programa.co
```

Los archivos con extensión ``.cobra`` representan paquetes completos, mientras que los scripts individuales se guardan como ``.co``.

El subcomando `docs` ejecuta `sphinx-apidoc` para generar la documentación de la API antes de compilar el HTML.
El subcomando `gui` abre el iddle integrado y requiere tener instalado Flet.

## Conversión desde otros lenguajes a Cobra

`cobra transpilar-inverso` documenta una capacidad distinta de la transpilación de salida normal. Aquí conviene separar dos listas para evitar ambigüedades:

- **Targets oficiales de salida**: consultar el resumen normativo generado al inicio de este README.
- **Orígenes reverse de entrada**: `python`, `javascript`, `java`.

Los nombres `python`, `javascript` y `java` aparecen en ambas listas, pero con papeles distintos: como `--origen` describen **entradas aceptadas** por la ruta reverse; como `--destino` vuelven a significar **targets oficiales de salida ya existentes**. La capacidad reverse no añade targets nuevos ni amplía la lista oficial de salida.

```bash
cobra transpilar-inverso script.py --origen=python --destino=python
```

El proceso intenta mapear instrucciones básicas, pero características muy específicas pueden requerir ajustes manuales. Actualmente la cobertura varía según el lenguaje y puede que ciertas construcciones no estén implementadas.

Actualmente la transpilación inversa soportada por política acepta código de entrada solo en la whitelist reverse oficial. Esos nombres son **orígenes reverse**, no destinos oficiales adicionales. Para el detalle normativo reutilizable consulta el resumen generado al inicio de este README y `docs/targets_policy.md`.

### Diseño extensible de la CLI

La CLI está organizada en clases dentro de `src/pcobra/cli/commands`. Cada subcomando
hereda de `BaseCommand` y define su nombre, los argumentos que acepta y la acción
a ejecutar. En `src/pcobra/cli/cli.py` se instancian automáticamente y se registran en
`argparse`, por lo que para añadir un nuevo comando solo es necesario crear un
archivo con la nueva clase y llamar a `register_subparser` y `run`.
Para un tutorial completo de creación de plugins revisa
[`docs/frontend/plugins.rst`](docs/frontend/plugins.rst).

## Modo seguro

El intérprete y la CLI ejecutan el código en modo seguro de forma predeterminada. Este modo valida el AST y prohíbe primitivas como `leer_archivo`, `escribir_archivo`, `obtener_url`, `hilo`, `leer`, `escribir`, `existe`, `eliminar` y `enviar_post`. El validador `ValidadorProhibirReflexion` también bloquea llamadas a `eval`, `exec` y otras funciones de reflexión, además de impedir el acceso a atributos internos. Asimismo, las instrucciones `import` solo están permitidas para módulos instalados o incluidos en `IMPORT_WHITELIST`. Antes de cargar el código las rutas se normalizan con `os.path.realpath` y se comparan con `os.path.commonpath`, por lo que un enlace simbólico o un directorio como `modules_fake` no pueden evadir el filtro. Si el programa intenta utilizar estas funciones o importar otros archivos se lanzará `PrimitivaPeligrosaError`.
La validación se realiza mediante una cadena de validadores configurada por la
función `construir_cadena`, lo que facilita añadir nuevas comprobaciones en el
futuro.

### Auditoría de eventos de seguridad en runtime

La CLI registra eventos de auditoría cuando se activan rutas críticas de la
política de seguridad (por ejemplo, `--no-seguro`, `--allow-insecure-fallback`
o un bloqueo en CI/no interactivo). Cada warning incluye:

- `event`: nombre del evento de seguridad.
- `command`: comando afectado.
- `reason`: motivo de la decisión.
- `audit_id`: identificador estable (`SEC-RUNTIME-001..005`).

En `text` (default), los campos van serializados en el propio mensaje para
facilitar parsing por regex. Para pipelines CI/SIEM puedes habilitar salida JSON
con `log_formatter = "json"` en `cobra-cli.toml` (o
`COBRA_LOG_FORMATTER=json`), obteniendo un objeto por línea.

## Ejecución en sandbox (--sandbox)

Algunos comandos permiten ejecutar código dentro de una sandbox o de contenedores Docker oficiales gracias
a la biblioteca `RestrictedPython`. Esto limita las operaciones disponibles y
evita acciones potencialmente peligrosas como leer archivos o importar módulos
externos. Para activar esta opción utiliza `--sandbox` en los subcomandos
`ejecutar` e `interactive`.

El código se compila con `compile_restricted` y luego se ejecuta mediante
`exec`. **No** se recurre a `compile()` cuando la compilación segura falla,
sino que se propaga la excepción. El uso de `exec` sigue siendo peligroso,
por lo que se recomienda mantener el entorno de ejecución lo más pequeño
posible para reducir riesgos.

# Pruebas

Las pruebas están ubicadas en la carpeta `tests/` y utilizan pytest para la
ejecución. **Antes de correr cualquier prueba instala el paquete en modo
editable junto con las dependencias de desarrollo:**

```bash
pip install -e .[dev]
```

Además, cada cambio en los workflows de GitHub Actions se valida con
[`actionlint`](https://github.com/rhysd/actionlint) mediante el workflow
[Validar workflows](.github/workflows/validate-workflows.yml). Este proceso se
ejecuta automáticamente en los eventos `push` y `pull_request` cuando se
modifican archivos dentro de `.github/workflows/`, evitando que se integren
definiciones inválidas en la canalización de CI.

Esta instrucción añade el proyecto al `PYTHONPATH` e instala todas las
dependencias listadas en `requirements-dev.txt`, generado desde el extra `dev`
de `pyproject.toml`. Sin estas bibliotecas las pruebas fallarán debido a
módulos no encontrados.

Si prefieres ejecutar las pruebas directamente desde el repositorio sin
instalar el paquete, utiliza el script `scripts/test.sh`:

```bash
./scripts/test.sh
```

Este comando exporta `PYTHONPATH=$PWD` e invoca `pytest` con los argumentos
definidos en `pyproject.toml`.

````bash
PYTHONPATH=$PWD pytest tests --cov=pcobra --cov-report=term-missing \
  --cov-fail-under=95
````

 Algunas pruebas generan código en distintos lenguajes (por ejemplo `cpp`, JavaScript o Go) y verifican que la sintaxis sea correcta. Para que estas pruebas se ejecuten con éxito es necesario contar con los compiladores o intérpretes correspondientes instalados en el sistema. En particular se requiere:

- Node.js
- gcc y g++
- Go (`golang-go`)
- Rust (`rustc`)
- Java (`default-jdk`)

Con estas herramientas disponibles puedes ejecutar todo el conjunto con:

```bash
PYTHONPATH=$PWD pytest
```

En la integración continua se emplea:

```bash
pytest --cov=pcobra tests/
```

El reporte se guarda como `coverage.xml` y se utiliza en el CI.

### Ejemplos de prueba

En `tests/data` se incluyen programas mínimos utilizados en las
pruebas de entrada y salida de la CLI:

- `hola.cobra`: imprime el saludo «Hola Cobra».
- `suma.cobra`: define la función `sumar` y muestra la suma de dos
  números.

El archivo `tests/test_ejemplos_io.py` ejecuta estos ejemplos y compara
la salida con los archivos `.out` correspondientes. Para probarlos
manualmente:

```bash
cobra ejecutar tests/data/hola.cobra
cobra ejecutar tests/data/suma.co
```

También puedes transpilar los ejemplos para ver el código Python generado:

```bash
cobra compilar tests/data/hola.cobra --backend python
cobra compilar tests/data/suma.co --backend python
```

#### Regenerar snapshots de transpilación (`tests/data/expected_examples`)

Cuando cambie el transpiler de Python, actualiza los snapshots esperados para los
ejemplos de `tests/data` (los que tienen archivo `.out` asociado):

1. Lista los ejemplos con salida esperada:

   ```bash
   python - <<'PY'
   from pathlib import Path
   base = Path("tests/data")
   print(sorted(p.stem for p in base.glob("*.out")))
   PY
   ```

2. Regenera cada snapshot `.py` ejecutando la CLI por archivo y copiando el
   bloque de código generado dentro de `tests/data/expected_examples/<nombre>.py`.
   Ejemplo manual:

   ```bash
   SQLITE_DB_KEY=test cobra transpilar tests/data/hola.cobra
   ```

3. Ejecuta la suite de ejemplos para validar que los snapshots quedaron alineados:

   ```bash
   PYTHONPATH=$PWD SQLITE_DB_KEY=test pytest tests/test_ejemplos_io.py
   ```

### Pruebas de rendimiento

El archivo `cobra.toml` incluye una sección `[rendimiento]` con el parámetro
`tiempo_max_transpilacion_seg`, que define en segundos el tiempo máximo
permitido para transpilar un archivo.

Para ejecutar únicamente las pruebas de rendimiento utiliza:

```bash
pytest -m performance
```

Si tu entorno es más lento o más rápido, ajusta el valor de
`tiempo_max_transpilacion_seg` en `cobra.toml` según tus necesidades.

Se han incluido pruebas que verifican los códigos de salida de la CLI. Los
subcomandos devuelven `0` al finalizar correctamente y un valor distinto en caso
de error.

### Comandos válidos por destino

La siguiente lista se generó a partir de `LANG_CHOICES` en `src/pcobra/cobra/cli/commands/compile_cmd.py`
(ordenada alfabéticamente) para mantener la documentación alineada con la CLI real:

````bash
cobra compilar programa.co --backend asm
cobra compilar programa.co --backend cpp
cobra compilar programa.co --backend go
cobra compilar programa.co --backend java
cobra compilar programa.co --backend javascript
cobra compilar programa.co --backend python
cobra compilar programa.co --backend rust
cobra compilar programa.co --backend wasm
````

### Ejemplos de subcomandos

````bash
cobra compilar programa.co --backend python
cobra compilar programa.co --backend rust
cobra compilar programa.co --backend javascript
cobra compilar programa.co --backend wasm
cobra compilar programa.co --backend go
cobra compilar programa.co --backend cpp
cobra compilar programa.co --backend java
cobra compilar programa.co --backend asm
echo $?  # 0 al compilar sin problemas

cobra ejecutar inexistente.co
# El archivo 'inexistente.co' no existe
echo $?  # 1
````

### Errores comunes

- `El archivo '<archivo>' no existe`: la ruta es incorrecta o el archivo no está disponible.
- `El módulo <nombre> no existe`: se intenta eliminar un módulo no instalado.
- `Primitiva peligrosa: <nombre>`: se usó una función restringida en modo seguro.
- `Acción de módulos no reconocida`: el subcomando indicado es inválido.

## Selección de idioma

La CLI utiliza `gettext` para mostrar los mensajes en distintos idiomas.
Puedes definir el idioma estableciendo la variable de entorno `COBRA_LANG`
o pasando el argumento `--lang` al ejecutar `cobra`.

```bash
COBRA_LANG=en cobra --ayuda
cobra --lang en compilar archivo.co
```

Si deseas añadir otro idioma, crea una carpeta `docs/frontend/locale/<cod>/LC_MESSAGES`
con los archivos `.po` de traducción y envía un pull request.

Para obtener un reporte de cobertura en la terminal ejecuta:

````bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=95
````

## Caché del AST y SQLitePlus

A partir de la migración a **SQLitePlus**, la caché incremental de AST y tokens
se almacena en una base de datos `SQLite` cifrada en lugar de archivos sueltos.
La ruta por defecto es `~/.cobra/sqliteplus/core.db`, que se crea
automáticamente al primer acceso. Para inicializar la conexión es obligatoria la
variable de entorno `SQLITE_DB_KEY`, cuyo valor actúa como clave de cifrado.
Si necesitas una ubicación distinta configura `COBRA_DB_PATH`; cuando se
proporciona, el valor de `SQLITE_DB_KEY` se mantiene como clave incluso si
contiene `/` u otros separadores.

> ⚠️ La CLI valida `SQLITE_DB_KEY` al arrancar y falla de forma explícita si no
> está definida. Solo en entorno de desarrollo/pruebas se permite la excepción
> controlada `COBRA_DEV_MODE=1`, que habilita una clave temporal de sesión.

```bash
# Ejemplo recomendado: clave aleatoria fuerte para uso local/CI
export SQLITE_DB_KEY="$(openssl rand -hex 32)"  # Obligatorio para abrir la base
export COBRA_DB_PATH="$HOME/.cobra/sqliteplus/core.db"  # Opcional; usa el
                                                        # valor por defecto
# Para despliegues sin cifrado puedes usar un prefijo explícito:
export SQLITE_DB_KEY="path:/var/cache/pcobra/core.db"
# Solo desarrollo/pruebas controladas:
export COBRA_DEV_MODE=1
```

Si necesitas ubicar la base de datos en otro sitio, ajusta `COBRA_DB_PATH` a la
ubicación deseada antes de ejecutar `cobra`. Como compatibilidad adicional, un
valor de `SQLITE_DB_KEY` que empiece por `path:` o `file:` se interpreta como
ruta explícita y desactiva el cifrado; en cualquier otro caso el valor se trata
como clave aunque contenga separadores y se emitirá una advertencia si parece
una ruta. La antigua variable
`COBRA_AST_CACHE` continúa disponible únicamente como alias de compatibilidad:
si la defines, el sistema derivará automáticamente una ruta `cache.db` en ese
directorio y mostrará una advertencia de depreciación.

### Limpieza y mantenimiento

El comando `cobra cache` sigue siendo el método soportado para borrar la caché y
ahora opera directamente sobre la base de datos. Incluye la opción `--vacuum`
para recompac tar la base tras la limpieza:

```bash
cobra cache --vacuum
```

### Migración de cachés JSON anteriores

Si conservas el directorio `cache/` con los archivos `.ast`/`.tok` utilizados en
versiones anteriores, puedes importarlos a SQLitePlus con el siguiente flujo:

1. Define `SQLITE_DB_KEY` (y `COBRA_DB_PATH` si deseas una ruta distinta).
2. Ejecuta el script auxiliar desde la raíz del proyecto, indicando la carpeta
   donde se encuentran los archivos heredados:

   ```bash
   python scripts/migrar_cache_sqliteplus.py --origen /ruta/al/cache
   ```

   El script convierte cada hash almacenado en JSON y recrea los fragmentos en
   la tabla SQLite. Las ejecuciones posteriores reutilizarán esa información sin
   necesidad de reanalizar tus fuentes.

3. Verifica la migración listando el contenido con cualquier visor SQLite o
   ejecutando nuevamente `cobra cache --vacuum` para comprobar que la conexión se
   inicializa correctamente.

Tras la migración, los ficheros JSON pueden eliminarse si ya no son necesarios.

## Generar documentación

Para obtener la documentación HTML puedes usar `cobra docs` o
`make html` desde la raíz del proyecto. El subcomando `docs` ejecuta
`sphinx-apidoc` y luego compila el HTML en la carpeta de salida configurada.

Puedes compilar la documentación de dos maneras:

1. **Con la CLI de Cobra**. Ejecuta `cobra docs`.

2. **Con Make**. Ejecuta `make html` para compilar los archivos ubicados en
   `docs/frontend`.

3. **Con pdoc**. Para generar documentación de la API con [pdoc](https://pdoc.dev),
   ejecuta `python scripts/generar_pdoc.py`. El resultado se guardará en
   la carpeta de salida configurada para la API.

A partir de esta versión, la API se genera de forma automática antes de
cada compilación para mantener la documentación actualizada.
Para aprender a desarrollar plugins revisa
[`docs/frontend/plugin_dev.rst`](docs/frontend/plugin_dev.rst).
Para conocer en detalle la interfaz disponible consulta
[`docs/frontend/plugin_sdk.rst`](docs/frontend/plugin_sdk.rst).

## Análisis con CodeQL

Este proyecto cuenta con un workflow de GitHub Actions definido en
`.github/workflows/codeql.yml`. Dicho flujo se ejecuta en cada *push* y
*pull request*, inicializando CodeQL para el lenguaje Python y aplicando
reglas personalizadas ubicadas en `.github/codeql/custom/`.

Las reglas proporcionan comprobaciones adicionales sobre el AST y los
transpiladores:

- **ast-no-type-validation.ql** verifica que las clases de nodos cuyo
  nombre empieza por `Nodo` incluyan validaciones de tipo en
  `__post_init__`.
- **missing-codegen-exception.ql** detecta métodos `generate_code` sin
  manejo de excepciones.
- **unsafe-eval-exec.ql** avisa cuando se usa `eval` o `exec` fuera del sandbox.

Para ejecutar el análisis de CodeQL de forma local puedes usar la CLI:

```bash
curl -L -o codeql.zip \
  https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip
unzip codeql.zip
./codeql/codeql database create db-python --language=python --source-root=.
./codeql/codeql database analyze db-python \
  .github/codeql/custom/codeql-config.yml
```

Esto te permitirá validar los cambios antes de subirlos al repositorio.
## Hitos y Roadmap

El proyecto avanza en versiones incrementales. Puedes consultar las tareas planeadas en [ROADMAP.md](docs/ROADMAP.md).


# Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, sigue estos pasos:

- Haz un fork del proyecto.
- Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`).
- Las ramas que comiencen con `feature/`, `bugfix/` o `doc/` recibirán etiquetas
  automáticas al abrir un pull request.
- Sigue las convenciones de estilo indicadas en `CONTRIBUTING.md`
  (formateo con `black`, longitud máxima de línea 88 y uso de `ruff`, `mypy`
  y `bandit`).
- Realiza tus cambios y haz commit (`git commit -m 'Añadir nueva característica'`).
- Ejecuta `make lint` para verificar el código con *ruff*, *mypy* y *bandit*. `bandit` analizará el directorio `src`.
- Ejecuta `make typecheck` para la verificación estática con *mypy* (y
  opcionalmente *pyright* si está instalado).
- Ejecuta primero el smoke de sintaxis con `python scripts/smoke_syntax.py`
  (sintaxis Python en `src/` y `tests/`, más parseo básico de fixtures Cobra).
- Ejecuta `python scripts/smoke_transpilers_syntax.py` para transpilación + validación
  sintáctica cruzada de los 8 targets oficiales (`python`, `javascript`, `rust`, `go`,
  `cpp`, `java`, `wasm`, `asm`) sobre fixtures `.co` mínimos. El script reporta por
  target `ok/fail/skipped` (cuando falta una dependencia externa como `node`, `rustc`,
  `javac`, etc.) y devuelve código de salida no-cero si falla algún target obligatorio.
- Ejecuta `make secrets` para buscar credenciales expuestas usando *gitleaks*.
- Para lanzar todas las validaciones en un solo paso ejecuta `python scripts/check.py`.
  Este script corre primero `smoke_syntax.py`, luego `smoke_transpilers_syntax.py`,
  y después *ruff*, *mypy*,
  *bandit*, *pyright* y *pytest*.
  Orden recomendado: **(1)** smoke sintaxis, **(2)** smoke transpiladores,
  **(3)** lint/tipos, **(4)**
  pruebas unitarias/integración.
  El umbral de cobertura que aplica `pytest` se toma de `pyproject.toml`
  (`tool.coverage.report.fail_under`), igual que en CI.
- El CI de GitHub Actions ejecuta automáticamente estas herramientas en cada pull request;
  para reproducir localmente la validación completa del pipeline usa `python scripts/check.py`.
- Envía un pull request.
- Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles sobre cómo abrir
  issues y preparar pull requests.
- Para proponer nuevas extensiones consulta [docs/frontend/rfc_plugins.rst](docs/frontend/rfc_plugins.rst).

## Dependabot y seguridad

Este repositorio cuenta con [Dependabot](.github/dependabot.yml) para mantener
actualizadas las dependencias de Python y las acciones de GitHub. Cada semana se
crean PR automáticos contra la rama `work` con las versiones más recientes.

Además, en el flujo de CI se incluye un paso de **safety check** que revisa la
lista de paquetes instalados en busca de vulnerabilidades conocidas. Si se
detecta alguna, la acción devolverá un reporte detallado y el trabajo fallará.
Consulta el log del paso "Seguridad de dependencias" para ver los paquetes
afectados y las recomendaciones de actualización.
De igual forma, se ejecuta *gitleaks* para asegurarse de que no existan
credenciales accidentales en el repositorio.

El repositorio también ejecuta CodeQL con reglas personalizadas para detectar
patrones de código riesgosos, como el uso de `eval` o `exec` fuera del sandbox.

## Comunidad

Únete a nuestro servidor de Discord para recibir anuncios, resolver dudas y colaborar en el desarrollo en [https://discord.gg/cobra](https://discord.gg/cobra).
También contamos con un canal de **Telegram** y una cuenta de **Twitter** donde difundimos eventos y actualizaciones.

## Desarrollo

Para verificar el tipado de forma local ejecuta:

```bash
mypy src
pyright
```

Tanto `mypy` como `pyright` utilizan la configuración presente en `pyproject.toml`.

Para ejecutar los linters puedes usar el comando de Make:

```bash
make lint
make secrets
```
El segundo comando ejecuta *gitleaks* para detectar posibles secretos en el repositorio.

Esto ejecutará `ruff` y `mypy` sobre `src`, y `bandit` revisará el directorio `src`. Si prefieres lanzar las herramientas de
manera individual utiliza:

```bash
ruff check src
mypy src
```

## Desarrollo de plugins

La CLI puede ampliarse mediante plugins externos. Desde esta versión todo el SDK
de plugins se encuentra en ``src.cobra.cli.plugin``. Para crear uno, define una clase
que herede de ``PluginCommand`` y declara el ``entry point`` en la sección
``[project.entry-points."cobra.plugins"]`` de tu ``pyproject.toml``. También es
necesario configurar un ``[build-system]`` moderno, como el basado en
``setuptools``:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project.entry-points."cobra.plugins"]
saludo = "mi_paquete.mi_modulo:SaludoCommand"
```

Tras instalar el paquete con `pip install -e .`, Cobra detectará automáticamente
el nuevo comando.

### Ejemplo de plugin

```python
from cobra.cli.plugin import PluginCommand


class HolaCommand(PluginCommand):
    name = "hola"
    version = "1.0"
    author = "Tu Nombre"
    description = "Dice hola desde un plugin"

    def register_subparser(self, subparsers):
        parser = subparsers.add_parser(self.name, help="Muestra un saludo")
        parser.set_defaults(cmd=self)

    def run(self, args):
        print("¡Hola desde un plugin!")
```
## Extensión para VS Code

La extensión para Visual Studio Code se encuentra en [`extensions/vscode`](extensions/vscode). Instala las dependencias con `npm install`. Desde VS Code puedes pulsar `F5` para probarla o ejecutar `vsce package` para generar el paquete `.vsix`. Consulta [extensions/vscode/README.md](extensions/vscode/README.md) para más detalles.

## Versionado Semántico

Este proyecto sigue el esquema [SemVer](https://semver.org/lang/es/). Los numeros se interpretan como Mayor.Menor.Parche. Cada incremento de version refleja cambios compatibles o rupturas segun esta norma.

## Historial de Cambios

 - Versión 10.0.12: migración de la caché incremental a SQLitePlus, nuevos helpers (`grupo_tareas`, `reintentar_async`, `prefijo_comun`, `interpolar`, `envolver_modular`) y soporte Parquet/Feather en la biblioteca estándar.

## Publicar una nueva versión

Al crear y subir una etiqueta `vX.Y.Z` se ejecuta el workflow [`release.yml`](.github/workflows/release.yml), que construye el paquete, los ejecutables y la imagen Docker.

El workflow [`Deploy Docs`](.github/workflows/pages.yml) generará la documentación cuando haya un push en `main` o al etiquetar una nueva versión.

Consulta la [guía de lanzamiento](docs/release.md) para más detalles sobre el etiquetado, secretos y el flujo de la pipeline.

```bash
git tag v10.0.12
git push origin v10.0.12
```

Para más información consulta el [CHANGELOG](CHANGELOG.md) y la [configuración de GitHub Actions](.github/workflows).

## Lenguajes soportados

- python
- rust
- javascript
- wasm
- go
- cpp
- java
- asm

Esta lista debe mantenerse sincronizada con la documentación en inglés. Consulta la [traducción al inglés](docs/README.en.md) para más detalles.

Separación normativa resumida: consulta el bloque generado al inicio de este README y la fuente canónica en `docs/targets_policy.md`.

# Licencia

Este proyecto está bajo la [Licencia MIT](LICENSE).


### Notas

- **Documentación y Ejemplos Actualizados**: El README ha sido actualizado para reflejar las capacidades de transpilación. Consulta la sección [Lenguajes soportados](#lenguajes-soportados) para ver la lista de lenguajes compatibles.
- **Ejemplos de Código y Nuevas Estructuras**: Incluye ejemplos con el uso de estructuras avanzadas como clases y diccionarios en el lenguaje Cobra.

Si deseas agregar o modificar algo, házmelo saber.
