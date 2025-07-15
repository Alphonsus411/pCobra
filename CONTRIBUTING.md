# Guía de Contribución

Gracias por tu interés en mejorar Cobra. A continuación se describen las pautas para participar en el proyecto.

## Reportar Issues

1. **Busca duplicados**: antes de abrir un issue verifica si alguien más ya ha reportado el mismo problema o solicitado la misma característica.
2. **Título claro**: usa un título descriptivo. Si es un error, añade un prefijo `[Bug]`.
3. **Información útil**: indica la versión de Cobra, sistema operativo y pasos detallados para reproducir el problema. Incluye el comportamiento esperado y lo que realmente ocurre.
4. **Etiquetas recomendadas**: usa `bug` para reportes de errores, `enhancement` para mejoras y `question` para dudas. Las peticiones de mejora de la documentación deben llevar la etiqueta `documentation`.
5. **Plantilla de documentación**: si abres un issue relacionado con la documentación, selecciona la plantilla **Documentación**.

## Convenciones de Estilo

- El codigo debe formatearse con `black` y respetar 88 caracteres por linea.
- Ejecuta `make lint` para comprobar `flake8`, `mypy` y `bandit`.
- Ejecuta `make secrets` para buscar credenciales expuestas con *gitleaks*.
- Usa `make typecheck` para la verificacion de tipos.
- Para analisis estatico con `pyright`, instala el paquete y ejecuta
  `pyright backend/src` (o `make typecheck`).
- Cualquier cambio en el lenguaje debe seguir lo descrito en
  [SPEC_COBRA.md](SPEC_COBRA.md).

## PYTHONPATH y PyCharm

Para que las importaciones `from src...` funcionen durante el desarrollo,
define el directorio `backend/src` en la variable `PYTHONPATH` o instala el
paquete en modo editable con `pip install -e .`:

```bash
export PYTHONPATH=$PWD/backend/src
```

En PyCharm marca `backend/src` como *Sources Root* para que resuelva las rutas
correctamente. Un ejemplo rápido de ejecución sería:

```bash
PYTHONPATH=$PWD/backend/src python -c "from src.core.main import main; main()"
```

## Ejecutar Pruebas

Las pruebas unitarias se ubican en `tests/unit` y las de integración en
`tests/integration`. Antes de ejecutarlas, establece `PYTHONPATH=$PWD/backend/src`
o instala el paquete en modo editable (`pip install -e .`). Para ejecutarlas
todas utiliza:

```bash
PYTHONPATH=$PWD/backend/src pytest
```

Para generar un reporte de cobertura:

```bash
PYTHONPATH=$PWD/backend/src pytest --cov
```

Además de las pruebas, ejecuta las verificaciones de estilo con:

```bash
make lint
```

## Pull Requests

1. **Fork y rama**: haz un fork y crea una rama a partir de `main` con el prefijo adecuado (`feature/`, `bugfix/` o `doc/`) y una breve descripcion. Esto permite que las acciones de GitHub etiqueten tu PR automáticamente.
2. **Sincroniza con `main`**: antes de abrir el PR, actualiza tu rama para incorporar los últimos cambios.
3. **Pruebas y estilo**: ejecuta `make lint` y `make typecheck` para asegurarte de que el código pasa las verificaciones. Añade o ajusta pruebas cuando sea necesario. Ejecuta además `make secrets` para comprobar que no se subieron credenciales.
4. **Descripción**: indica el propósito del cambio y referencia issues relacionados usando `#numero`.
5. **Etiquetas de PR**: añade `enhancement`, `bug`, `documentation` u otra etiqueta que describa el cambio.
6. **Revisión**: una vez abierto el PR, espera la revisión de los mantenedores y realiza los cambios solicitados.

¡Agradecemos todas las contribuciones!

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
