# Guía de Lanzamiento

## Etiquetar una versión

1. Asegúrate de que `main` contenga los cambios que deseas publicar.
2. Crea una etiqueta semántica y súbela al repositorio:

```bash
 git tag vX.Y.Z
 git push origin vX.Y.Z
```

 También puedes subir todas las etiquetas existentes con:

```bash
 git push --tags
```

## Secretos requeridos

Los workflows de publicación utilizan los siguientes secretos configurados en el repositorio:

- `PYPI_USERNAME` y `PYPI_PASSWORD`: credenciales para subir el paquete a PyPI.
- `DOCKERHUB_USERNAME` y `DOCKERHUB_TOKEN`: acceso para publicar la imagen en Docker Hub.
- `SLACK_WEBHOOK_URL`: webhook para notificaciones en Slack.
- Credenciales SMTP (`SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_HOST`, `SMTP_PORT`): envío de correos electrónicos.

## Flujo de la pipeline

Al crear una etiqueta `vX.Y.Z` se ejecuta el workflow [`release.yml`](../.github/workflows/release.yml) que:

1. Construye y publica el paquete en PyPI.
2. Genera los ejecutables y los adjunta a GitHub Releases.
3. Construye y sube la imagen Docker.
4. Publica la documentación.
5. Envía notificaciones a Slack y correo electrónico si corresponde.

Consulta el [archivo del workflow](../.github/workflows/release.yml) para más detalles.


## Checklist de release: árbol limpio de lenguajes no oficiales

Antes de etiquetar una versión, confirma explícitamente:

- [ ] No hay referencias activas en código, ejemplos o scripts a lenguajes fuera del set oficial de salida (`python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java`, `asm`).
- [ ] No hay referencias activas en reverse fuera del set oficial de entrada (`python`, `javascript`, `java`).
- [ ] `examples/`, `extensions/`, `scripts/benchmarks/` y `docker/` están alineados con el alcance oficial.
- [ ] Se ejecutó un barrido final de cadenas y rutas para detectar residuos antes de publicar.


## Checklist de release notes (equipo Holobit)

Antes de publicar una versión con cambios de política de targets:

- [ ] Confirmar que la narrativa pública mantiene exclusivamente los 8 targets canónicos de salida.
- [ ] Incluir la nota de corrección: la CLI instalada ya no importa `scripts.benchmarks` en tiempo de ejecución (usa `pcobra.cobra.benchmarks`).
- [ ] Adjuntar pasos de migración vigentes para CI/scripts (`--backend`, `--tipo`, `--tipos`).
- [ ] Ejecutar `python scripts/audit_retired_targets.py <ruta_proyecto>` sobre repos de referencia del ecosistema.
- [ ] Coordinar copy final con equipo Holobit y validar FAQ de impacto:
  `docs/compatibility/holobit_target_deprecation_faq.md`.
- [ ] Si se necesita detallar cronología o aliases históricos, enlazar archivo histórico en lugar de incorporarlo al flujo activo:
  `docs/historico/migracion_targets_retirados_archivo.md`.
