# Guía de Contribución

Gracias por tu interés en mejorar Cobra. A continuación se describen las pautas para participar en el proyecto.

## Reportar Issues

1. **Busca duplicados**: antes de abrir un issue verifica si alguien más ya ha reportado el mismo problema o solicitado la misma característica.
2. **Título claro**: usa un título descriptivo. Si es un error, añade un prefijo `[Bug]`.
3. **Información útil**: indica la versión de Cobra, sistema operativo y pasos detallados para reproducir el problema. Incluye el comportamiento esperado y lo que realmente ocurre.
4. **Etiquetas recomendadas**: usa `bug` para reportes de errores, `enhancement` para mejoras y `question` para dudas. Las peticiones de mejora de la documentación deben llevar la etiqueta `documentation`.
5. **Plantilla de documentación**: si abres un issue relacionado con la documentación, selecciona la plantilla **Documentación**.

## Clasificación de Issues por nivel

Para agilizar la organización del proyecto, categoriza cada tarea utilizando las etiquetas de dificultad:

- `facil` para cambios menores o de documentación.
- `medio` para implementaciones de complejidad moderada.
- `avanzado` cuando el issue implique refactorizaciones importantes o trabajo extenso.

## Tareas para nuevos contribuidores

Las tareas etiquetadas como `good first issue` están orientadas a la comunidad y se consideran de baja prioridad. Se seleccionan entre los issues marcados con `facil` o `low priority` en el directorio `docs/issues/`. Los mantenedores revisan periódicamente esta lista para asegurarse de que sigan siendo sencillas de abordar y actualizan o retiran la etiqueta cuando sea necesario.

## Convenciones de Estilo

- El codigo debe formatearse con `black` y respetar 88 caracteres por linea.
- Ejecuta `make lint` para comprobar `ruff`, `mypy` y `bandit`.
- Ejecuta `make secrets` para buscar credenciales expuestas con *gitleaks*.
- Usa `make typecheck` para la verificacion de tipos.
- Para analisis estatico con `pyright`, instala el paquete y ejecuta
  `pyright src` (o `make typecheck`).
- Cualquier cambio en el lenguaje debe seguir lo descrito en
  [SPEC_COBRA.md](docs/SPEC_COBRA.md).

## Dependencias y versionado

- Mantén sincronizadas las versiones fijadas en `pyproject.toml`,
  `requirements.txt` y `requirements-dev.txt`. Cuando se actualice una
  dependencia, revisa los tres archivos y aplica el mismo número de versión.
- En particular, la versión soportada de `requests` se define en `pyproject.toml`
  y debe replicarse en los archivos de requirements para evitar divergencias.
- Tras modificar requisitos, ejecuta `cobra dependencias listar` (o una
  instalación de prueba con `pip install -r requirements.txt`) para comprobar
  que no existan entradas duplicadas o incompatibles.

## PYTHONPATH y PyCharm

Para que las importaciones `from src...` funcionen durante el desarrollo,
define el directorio `src` en la variable `PYTHONPATH` o instala el
paquete en modo editable con `pip install -e .`:

```bash
export PYTHONPATH=$PWD/src
```

En PyCharm marca `src` como *Sources Root* para que resuelva las rutas
correctamente. Un ejemplo rápido de ejecución sería:

```bash
PYTHONPATH=$PWD/src python -c "from src.core.main import main; main()"
```

## Ejecutar Pruebas

Las pruebas unitarias se ubican en `tests/unit` y las de integración en
`tests/integration`. Antes de ejecutarlas, establece `PYTHONPATH=$PWD/src`,
instala el paquete en modo editable (`pip install -e .`) y ejecuta
`./scripts/install_dev.sh` para instalar las dependencias. Para ejecutarlas
todas utiliza:

```bash
PYTHONPATH=$PWD/src pytest
```

Para generar un reporte de cobertura:

```bash
PYTHONPATH=$PWD/src pytest --cov
```

Además de las pruebas, ejecuta las verificaciones de estilo con:

```bash
make lint
```

### Orden recomendado de validaciones locales

Para iterar más rápido y detectar errores temprano, ejecuta las validaciones
en este orden:

1. **Smoke de sintaxis**: `python scripts/smoke_syntax.py`
   - Compila sintaxis Python en `src/` y `tests/`.
   - Ejecuta parseo básico de fixtures `.co` representativos.
2. **Lint y tipos**: `make lint` y `make typecheck` (opcional `pyright src`).
3. **Pruebas unitarias/integración**: `PYTHONPATH=$PWD/src pytest`.

Si prefieres un solo comando secuencial, usa `python scripts/check.py`, que
sigue este mismo orden.

Cada workflow en `.github/workflows` se valida automáticamente mediante el
test `tests/test_workflows_yaml.py`. Si añades o modificas un workflow,
ejecuta `pytest` para asegurarte de que el archivo es YAML válido antes de
subir los cambios.
## Pruebas de transpiladores

Las pruebas de los transpiladores ejecutan el código generado en varios lenguajes.
Para que funcionen es necesario tener instalados en el sistema los intérpretes o
compiladores correspondientes y accesibles desde `PATH`:

- Python 3
- Node.js
- Go
- Rust (`rustc`)
- Java (`javac`)
- C++ (`g++` o `clang++`)

Puedes ejecutar únicamente estas pruebas con:

```bash
PYTHONPATH=$PWD/src pytest tests/integration/test_runtime_*
```

Para correr todo el conjunto de pruebas, incluidas las anteriores:

```bash
PYTHONPATH=$PWD/src pytest
```

### Checklist: árbol limpio de lenguajes no oficiales

Antes de abrir un PR que toque transpilación, ejemplos, extensiones o imágenes Docker, verifica:

- [ ] No se añadieron referencias a targets fuera de la política oficial (`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`).
- [ ] No se añadieron referencias de `transpilar-inverso` fuera de los orígenes oficiales (`python`, `javascript`, `java`).
- [ ] `examples/`, `extensions/`, `scripts/benchmarks/` y `docker/` no contienen archivos huérfanos de lenguajes fuera de alcance.
- [ ] Se ejecutó un barrido de cadenas/rutas para detectar menciones residuales antes de enviar cambios.

### Regla de mantenimiento coordinado para targets oficiales

El conjunto oficial actual de backends públicos es:

- `python`
- `rust`
- `javascript`
- `wasm`
- `go`
- `cpp`
- `java`
- `asm`

Lista oficial por tiers:

- **Tier 1**: `python`, `rust`, `javascript`, `wasm`.
- **Tier 2**: `go`, `cpp`, `java`, `asm`.

Y el alcance reverse oficial actual es:

- `python`
- `javascript`
- `java`

La CI valida automáticamente que no aparezcan artefactos de backends no oficiales
o aliases públicos no permitidos en:

- `src/pcobra/cobra/transpilers/transpiler/`
- `src/pcobra/cobra/transpilers/reverse/`
- `src/pcobra/cobra/transpilers/registry.py`
- `tests/integration/transpilers/golden/`
- `scripts/benchmarks/`
- documentación pública y rutas vigiladas por `scripts/ci/validate_targets.py`

Esto incluye nombres de archivo, imports Python, tablas de registro, snapshots
golden, scripts auxiliares y texto público.

Si en el futuro se amplía o cambia el conjunto oficial, **no basta** con añadir
un módulo nuevo. El cambio debe actualizar de forma coordinada:

1. Código fuente y registros canónicos (`targets`, `registry`, reverse policy, CLI).
2. Tests y snapshots (`golden`, fixtures, ayudas de runtime y benchmarks).
3. Documentación pública.
4. Reglas de CI, en especial `scripts/ci/validate_targets.py`.

Si falta cualquiera de esas piezas, la validación debe fallar y el cambio no debe
considerarse completo.

### Política de soporte por tiers (SLA)

Definición operativa para incidencias de regresión (transpilación, ayuda CLI o documentación de targets):

- **Tier 1**: triage inicial en <= 2 días hábiles.
- **Tier 2**: triage inicial en <= 5 días hábiles.

Criterios de promoción/degradación:

- **Promoción (Tier 2 → Tier 1)**: uso sostenido, estabilidad contractual y cobertura CI mantenida durante al menos dos releases consecutivas.
- **Degradación (Tier 1 → Tier 2)**: incumplimiento sostenido de calidad/CI, bloqueo de dependencias o desviación contractual repetida.

En ambos casos, el cambio exige RFC aprobada, plan de migración y comunicación en changelog/notas de release.

### Checklist corta: si tocas targets, regenera docs + valida CI de targets

- [ ] Ejecuté `python scripts/generate_target_policy_docs.py`.
- [ ] Ejecuté `python scripts/generar_matriz_transpiladores.py`.
- [ ] Verifiqué que no quedan diffs sin commitear en docs generadas de targets.
- [ ] Validé CI de targets (`python scripts/ci/validate_targets.py` y `python scripts/ci/ensure_generated_targets_docs_clean.py`).

### Gate de auditoría de contrato de targets (obligatorio en CI)

La CI ejecuta además `python scripts/ci/audit_targets_contract.py` como paso
bloqueante. Este gate valida automáticamente:

1. Set canónico de targets oficiales (`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`).
2. Coherencia entre `targets.py`, `registry.py` y `target_policies.py`.
3. Consistencia documental mínima, con barrido de términos no permitidos en documentación/workflows.
4. Regla de mantenimiento de matriz: si cambia
   `src/pcobra/cobra/transpilers/compatibility_matrix.py`, el PR también debe
   incluir cambios en tests de contrato y documentación contractual mínima.

Antes de abrir PR, ejecútalo localmente:

```bash
python scripts/ci/audit_targets_contract.py
```

Si quieres simular la comparación de un PR contra `main`, puedes pasar SHAs:

```bash
python scripts/ci/audit_targets_contract.py <base_sha> <head_sha>
```

### Añadir soporte para nuevos lenguajes en `run_code`

1. Crea una función `_run_<lenguaje>` en `tests/utils/runtime.py` que invoque
   al intérprete o compilador externo y devuelva la salida estándar.
2. Registra esa función en el diccionario `_RUNNERS` usando como clave el nombre
   del lenguaje.
3. Llama a `run_code("<lenguaje>", codigo)` en los tests para validar el
   comportamiento.

## Revisar logs de GitHub Actions

Cuando una tarea falla en CI dirígete a la pestaña *Actions* del repositorio y abre el flujo asociado a tu commit. Cada trabajo muestra los pasos ejecutados y permite desplegar los registros completos. Utiliza la barra de búsqueda para filtrar por palabras clave como `pytest` o `lint`. Desde **View raw logs** puedes descargar el archivo para analizarlo con mayor detalle.

Para reproducir los errores comunes ejecuta localmente:

```bash
pytest -vv
make lint
make typecheck
make secrets     # analiza con gitleaks
safety check --full-report
```


## Pull Requests

1. **Fork y rama**: haz un fork y crea una rama a partir de `main` con el prefijo adecuado (`feature/`, `bugfix/` o `doc/`) y una breve descripcion. Esto permite que las acciones de GitHub etiqueten tu PR automáticamente.
2. **Sincroniza con `main`**: antes de abrir el PR, actualiza tu rama para incorporar los últimos cambios.
3. **Pruebas y estilo**: ejecuta `make lint` y `make typecheck` para asegurarte de que el código pasa las verificaciones. Añade o ajusta pruebas cuando sea necesario. Ejecuta además `make secrets` para comprobar que no se subieron credenciales.
4. **Descripción**: indica el propósito del cambio y referencia issues relacionados usando `#numero`.
5. **Etiquetas de PR**: añade `enhancement`, `bug`, `documentation` u otra etiqueta que describa el cambio.
6. **Revisión**: una vez abierto el PR, espera la revisión de los mantenedores y realiza los cambios solicitados.

Checklist de PR para política de targets (bloqueante)

- [ ] Validé que el PR no introduce referencias públicas a targets fuera de contrato (nombres, aliases, comandos o ejemplos).
- [ ] Ejecuté `python scripts/ci/validate_targets.py` y no quedaron errores.
- [ ] Si toqué docs/CLI/ejemplos de targets, regeneré artefactos con `python scripts/generate_target_policy_docs.py`.
- [ ] Confirmé que los snippets de CLI usan únicamente targets canónicos oficiales.

¡Agradecemos todas las contribuciones!

## Actualizar CHANGELOG

Cada release debe incluir una entrada en `CHANGELOG.md` con el formato:

```
## vX.Y.Z - YYYY-MM-DD
- Descripción breve de los cambios.
```

Asegúrate de reemplazar cualquier marcador provisional como `Cambios pendientes.`
por una lista clara de mejoras o correcciones. Ejecuta `python scripts/check_changelog.py`
para validar que la última versión esté documentada antes de fusionar la rama.

## Mensajes de Commit

Seguimos la convención [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/), que define un formato estructurado para los mensajes. Cada commit debe comenzar con un **tipo**, un alcance opcional y una breve descripción en presente.

Ejemplos de mensajes válidos:

- `feat: agrega soporte para módulos personalizables`
- `fix(ci): corrige la ruta de despliegue`
- `docs: actualiza guía de instalación`

Consulta la [documentación oficial de Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/) para más detalles.

Recuerda ejecutar `make lint` antes de enviar tu pull request.

## Contacto

Si tienes dudas o necesitas ayuda, únete a nuestro canal comunitario en Discord (enlace disponible próximamente).

## Uso de stubs internos para dependencias opcionales

Para evitar colisiones con paquetes de terceros, los stubs del proyecto viven en
`pcobra/_stubs/` y **no** deben publicarse como paquetes top-level (`numpy`,
`pandas`, `rich`, `pexpect`, etc.).

### Estrategia obligatoria de importación

Cuando un módulo dependa de una librería opcional, sigue esta secuencia:

1. Intentar importar la librería real.
2. Hacer fallback al stub interno **solo** cuando:
   - el error sea `ModuleNotFoundError` del módulo objetivo, y
   - el fallback esté marcado como seguro.

Para ello usa `pcobra._stubs.compat` (`import_optional_module` o
`import_optional_attr`) con `safe_stub=True` únicamente en dependencias
aprobadas para fallback.

### Cuándo usar stubs

- Pruebas en entornos mínimos sin dependencias pesadas.
- Compatibilidad de utilidades no críticas donde existe una implementación
  reducida y documentada.

### Limitaciones de los stubs

- No replican toda la API de la librería real.
- Su comportamiento está acotado a los casos que usa actualmente el proyecto.
- No deben usarse para evaluar rendimiento ni compatibilidad completa.
- Si una funcionalidad requiere APIs avanzadas, instala la dependencia real en
  lugar de ampliar el stub sin justificación.
