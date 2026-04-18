# Configuración de la CLI

La configuración de Cobra se documenta en dos bloques para evitar mezclar onboarding de usuario con rutas internas de migración.

## 1) Configuración pública (usuarios)

Esta sección es la que forma parte del contrato público para quienes usan Cobra en el día a día con la ruta principal:

- `cobra run`
- `cobra build`
- `cobra test`
- `cobra mod`

## Archivo de configuración

- **Nombre:** `cobra-cli.toml`
- **Ubicación:** directorio de trabajo desde el que se ejecuta `cobra`.

## Claves públicas soportadas

| Clave            | Valor por defecto                                    | Descripción                                           |
|------------------|------------------------------------------------------|-------------------------------------------------------|
| `language`       | `es`                                                 | Idioma de la interfaz de la CLI.                      |
| `default_command`| `run`                                               | Subcomando ejecutado si no se especifica otro.        |
| `log_format`     | `%(asctime)s - %(levelname)s - %(message)s`          | Formato para los mensajes de registro (*logging*).    |
| `log_formatter`  | `text`                                                | Formato del handler raíz: `text` (default) o `json`.  |
| `program_name`   | `cobra`                                              | Nombre con el que aparece la aplicación en la ayuda.  |

Variables de entorno equivalentes: `COBRA_LANG`, `COBRA_DEFAULT_COMMAND`, `COBRA_LOG_FORMAT`, `COBRA_LOG_FORMATTER` y `COBRA_PROGRAM_NAME`.

## Eventos de auditoría de seguridad (públicos)

Cuando la CLI detecta rutas críticas de seguridad en runtime, emite warnings con campos estructurados para auditoría:

- `event`: tipo de evento de seguridad.
- `command`: subcomando activo.
- `reason`: causa concreta de la decisión.
- `audit_id`: identificador estable de auditoría (`SEC-RUNTIME-00x`).

En modo `text`, el `msg` incluye los campos en línea.
En modo `json` (`log_formatter = "json"` o `COBRA_LOG_FORMATTER=json`), el handler escribe un objeto JSON por línea apto para pipelines CI/SIEM.

## Ejemplo público

```toml
# cobra-cli.toml
language = "en"
default_command = "run"
log_format = "%(levelname)s: %(message)s"
log_formatter = "json"
program_name = "cobra"
```

Otro ejemplo mínimo:

```toml
language = "es"
program_name = "cobra-cli"
```

## 2) Opciones internas de migración (NO PÚBLICO)

> ⚠️ **NO PÚBLICO / SOLO MANTENEDORES**: lo siguiente existe para compatibilidad histórica, migraciones graduales y operación interna. No es material de onboarding para usuarios nuevos.

### Modos de operación (`--modo`)

El flag global `--modo` delimita internamente qué tipo de acciones permite la sesión (`cobra`, `transpilar`, `mixto`).

### Política de seguridad para `SQLITE_DB_KEY` en rutas internas

Para comandos con base de datos (`cache`, `build`, `benchtranspilers`, `qualia`, `interactive`), la CLI exige `SQLITE_DB_KEY`.

En desarrollo local controlado existe una ruta efímera con triple confirmación explícita (`COBRA_DEV_MODE=1`, `COBRA_DEV_ALLOW_EPHEMERAL_KEY=1`, `--dev-ephemeral-key`), reservada a escenarios de desarrollo interno.

### Mappings multi-backend en `cobra.toml`

La resolución multi-backend de módulos usa la tabla canónica `[modulos."..."]` y validación con `PUBLIC_BACKENDS` (`python`, `javascript`, `rust`).

### Política de colisiones de imports en `cobra.toml`

El resolvedor conserva precedencia estable: `stdlib > project > python_bridge > hybrid`, con políticas `warn`, `strict_error`, `namespace_required`.

### Política de targets oficial

La fuente de verdad para targets públicos es `src/pcobra/cobra/architecture/backend_policy.py` mediante `PUBLIC_BACKENDS`; `INTERNAL_BACKENDS` se reserva para compatibilidad legacy interna.

## Cómo elige backend Cobra internamente

Cobra decide backend como parte de su orquestación interna, sin exigir que la persona usuaria gestione flags de backend ni se acople a detalles de transpiladores.

Flujo de decisión de alto nivel:

1. Detecta contexto del proyecto y metadatos disponibles.
2. Evalúa el tipo de operación solicitada (`run`, `build`, `test`, `mod`).
3. Selecciona automáticamente un backend oficial compatible.
4. Ejecuta el pipeline interno manteniendo la UX pública estable (`run/build/test/mod`).

Regla de documentación: para usuarios finales, la guía siempre debe priorizar la interfaz pública y evitar exponer rutas legacy de migración como flujo normal.
