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
- Ruby

Puedes ejecutar únicamente estas pruebas con:

```bash
PYTHONPATH=$PWD/src pytest tests/integration/test_runtime_*
```

Para correr todo el conjunto de pruebas, incluidas las anteriores:

```bash
PYTHONPATH=$PWD/src pytest
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
