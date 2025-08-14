# Comunidad

Este proyecto cuenta con un servidor en Discord donde los usuarios pueden comunicarse, resolver dudas y colaborar en el desarrollo de Cobra.

## Roles
- **Administradores**: gestionan el servidor y velan por el cumplimiento de las normas.
- **Colaboradores**: participan activamente en el desarrollo y ayudan a otros miembros.

## Normas de convivencia
1. Respeta a todos los miembros de la comunidad.
2. Evita cualquier tipo de lenguaje ofensivo o discriminatorio.
3. Publica tus preguntas en el canal correspondiente para mantener el orden.
4. No hagas spam ni promociones no autorizadas.

## Cómo unirse
Únete a nuestro servidor en [Discord](https://discord.gg/pcobra) para participar en la comunidad y resolver dudas.

## Difusión de eventos
- Las convocatorias se anuncian en nuestro nuevo canal de **Telegram**.
- También publicamos novedades en la cuenta oficial de **Twitter**.

## Difusión
En esta sección se listarán los enlaces a hilos de Reddit, Dev.to y GitHub Discussions relacionados con el proyecto.

## Publicar entradas en el blog

El proyecto incluye un script para subir contenido Markdown al blog oficial.

### Variables de entorno
- `BLOG_API_URL`: URL del endpoint al que se enviará el contenido.
- `BLOG_API_TOKEN`: token de autenticación para el servicio.

### Ejecución
Define las variables anteriores y ejecuta:

```bash
scripts/publicar_blog.sh ruta/al/archivo.md
```

También puede ejecutarse mediante Make:

```bash
make publicar-blog FILE=ruta/al/archivo.md
```
