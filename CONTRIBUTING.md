# Guía de Contribución

Gracias por tu interés en mejorar Cobra. A continuación se describen las pautas para participar en el proyecto.

## Reportar Issues

1. **Busca duplicados**: antes de abrir un issue verifica si alguien más ya ha reportado el mismo problema o solicitado la misma característica.
2. **Título claro**: usa un título descriptivo. Si es un error, añade un prefijo `[Bug]`.
3. **Información útil**: indica la versión de Cobra, sistema operativo y pasos detallados para reproducir el problema. Incluye el comportamiento esperado y lo que realmente ocurre.
4. **Etiquetas recomendadas**: usa `bug` para reportes de errores, `enhancement` para mejoras y `question` para dudas. Si se trata de documentación, utiliza `documentation`.

## Pull Requests

1. **Fork y rama**: haz un fork y crea una rama a partir de `main` con el prefijo adecuado (`feature/`, `bugfix/` o `doc/`). Esto permite que las acciones de GitHub etiqueten tu PR automáticamente.
2. **Sincroniza con `main`**: antes de abrir el PR, actualiza tu rama para incorporar los últimos cambios.
3. **Pruebas y estilo**: ejecuta `make lint` y `make typecheck` para asegurarte de que el código pasa las verificaciones. Añade o ajusta pruebas cuando sea necesario.
4. **Descripción**: indica el propósito del cambio y referencia issues relacionados usando `#numero`.
5. **Revisión**: una vez abierto el PR, espera la revisión de los mantenedores y realiza los cambios solicitados.

¡Agradecemos todas las contribuciones!
