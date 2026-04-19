# Configuración de la CLI

La interfaz de línea de comandos de Cobra puede personalizarse mediante un archivo de configuración.

## Modos de operación (`--modo`)

El flag global `--modo` delimita qué tipo de acciones permite la sesión:

- `cobra`: solo ejecución/interpretación de programas Cobra.
- `transpilar`: solo generación de código (transpilación).
- `mixto` (por defecto): permite ambos flujos.

Ejemplos concretos:

```bash
cobra --modo cobra --ui v2 run programa.co
cobra --modo transpilar compilar programa.co --backend python
```

## Ruta del archivo

- **Nombre:** `cobra-cli.toml`
- **Ubicación:** directorio de trabajo desde el que se ejecuta `cobra`.

## Claves soportadas

| Clave            | Valor por defecto                                    | Descripción                                           |
|------------------|------------------------------------------------------|-------------------------------------------------------|
| `language`       | `es`                                                 | Idioma de la interfaz de la CLI.                      |
| `default_command`| `interactive`                                       | Subcomando ejecutado si no se especifica otro.        |
| `log_format`     | `%(asctime)s - %(levelname)s - %(message)s`          | Formato para los mensajes de registro (*logging*).    |
| `log_formatter`  | `text`                                                | Formato del handler raíz: `text` (default) o `json`.  |
| `program_name`   | `cobra`                                              | Nombre con el que aparece la aplicación en la ayuda.  |

Las variables de entorno `COBRA_LANG`, `COBRA_DEFAULT_COMMAND`, `COBRA_LOG_FORMAT`, `COBRA_LOG_FORMATTER` y `COBRA_PROGRAM_NAME` permiten sobrescribir estos valores.

## Eventos de auditoría de política de seguridad

Cuando la CLI detecta rutas críticas de seguridad en runtime, emite warnings con
campos estructurados para auditoría:

- `event`: tipo de evento de seguridad.
- `command`: subcomando activo.
- `reason`: causa concreta de la decisión.
- `audit_id`: identificador estable de auditoría (`SEC-RUNTIME-00x`).

En modo `text`, el `msg` incluye los campos en línea:

```text
security_policy_warning event=insecure_fallback command=run reason=explicit_allow_insecure_fallback audit_id=SEC-RUNTIME-003
```

En modo `json` (`log_formatter = "json"` o `COBRA_LOG_FORMATTER=json`), el
handler escribe un objeto JSON por línea apto para pipelines CI/SIEM.

## Política de seguridad para `SQLITE_DB_KEY` en la CLI

Para comandos que requieren base de datos (`cache`, `build`, `benchtranspilers`,
`qualia`, `interactive`), la CLI exige `SQLITE_DB_KEY`.

- **Producción/CI recomendado:** exporta siempre una clave real (`SQLITE_DB_KEY`)
  gestionada por tu secret manager.
- **Desarrollo local controlado:** se permite clave efímera **solo** con triple
  confirmación explícita en la misma ejecución:
  1. `COBRA_DEV_MODE=1`
  2. `COBRA_DEV_ALLOW_EPHEMERAL_KEY=1`
  3. flag CLI `--dev-ephemeral-key`

Cuando se cumplen las tres condiciones, la CLI genera una clave nueva por
ejecución con `secrets.token_urlsafe(...)` y registra un warning de seguridad no
sensible indicando que se está usando una clave efímera de desarrollo.

### Ejemplos seguros de arranque local

#### Opción A (preferida): clave explícita

```bash
export SQLITE_DB_KEY="$(python - <<'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
)"

cobra --ui v2 build ejemplo.co
```

#### Opción B (solo dev local): clave efímera por ejecución

```bash
COBRA_DEV_MODE=1 \
COBRA_DEV_ALLOW_EPHEMERAL_KEY=1 \
cobra --dev-ephemeral-key --ui v2 build ejemplo.co
```

> Nota: evita esta opción en CI/prod; está diseñada únicamente para sesiones
> locales temporales.

## Ejemplo

```toml
# cobra-cli.toml
language = "en"
default_command = "compile"
log_format = "%(levelname)s: %(message)s"
log_formatter = "json"
program_name = "cobra"
```

Otro ejemplo mínimo:

```toml
language = "es"
program_name = "cobra-cli"
```

## Mappings multi-backend en `cobra.toml`

Para resolver imports de módulos transpilados en varios backends, define rutas por
backend en `cobra.toml` bajo la tabla canónica `[modulos."..."]`. La resolución
multi-backend ya no usa `cobra.mod`, `pcobra.toml` ni mappings en raíz.

```toml
[project]
required_targets = ["python", "javascript"]

[modulos."modulo.co"]
python = "build/modulo.py"
rust = "build/modulo.rs"
javascript = "build/modulo.js"
```

### Reglas de validación

- Solo se aceptan nombres canónicos contenidos en `PUBLIC_BACKENDS`:
  `python`, `javascript` y `rust`.
- Los aliases legacy, abreviaturas históricas y traducciones antiguas de nombres de backend no son válidos; usa siempre los identificadores canónicos públicos.
- Los mappings de módulos deben vivir dentro de `[modulos."..."]`; las estructuras en raíz ya no se resuelven.
- `cobra.mod` sigue siendo el archivo validado por `modulos`/empaquetado, pero sus backends públicos deben respetar exclusivamente `PUBLIC_BACKENDS`.

### ¿Qué targets pueden omitirse intencionalmente?

- Puedes omitir cualquier target **no incluido** en `required_targets`.
- Si no declaras política, la validación asume por defecto el Tier 1 público completo: `python`, `javascript` y `rust`.
- Para proyectos que solo distribuyen un subconjunto de backends, ajusta
  explícitamente `required_targets` para evitar errores de validación.

## Terminología: interfaz pública vs backend interno

- **Interfaz pública**: comandos y documentación para usuarios (`cobra --ui v2 run`, `cobra --ui v2 build`, `cobra --ui v2 test`, `cobra --ui v2 mod`) y backends oficiales `python`, `javascript`, `rust`.
- **Backend interno**: rutas de compatibilidad o migración usadas por mantenedores, fuera del contrato público.

Toda referencia en documentación de usuario debe priorizar la terminología de interfaz pública.

## Política de targets oficial

La CLI no debe mantener listas duplicadas de lenguajes soportados. La fuente de
verdad para los targets públicos es
`src/pcobra/cobra/architecture/backend_policy.py` a través de
`PUBLIC_BACKENDS` (y `INTERNAL_BACKENDS` para legacy interno). La documentación
pública y los archivos de configuración deben usar únicamente los nombres
canónicos `python`, `javascript` y `rust`.

En consecuencia:

- `cobra build` debe derivar `TRANSPILERS` y `LANG_CHOICES` desde
  `PUBLIC_BACKENDS` y un registro canónico compartido.
- Los scripts auxiliares, especialmente benchmarks y validaciones CI, deben
  reutilizar utilidades comunes basadas en esa misma política.
- Cualquier nuevo backend oficial requiere actualizar primero esa fuente única y
  después el registro canónico correspondiente; no se permiten listas
  hardcodeadas duplicadas en la CLI o en scripts.
