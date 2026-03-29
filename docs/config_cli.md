# Configuración de la CLI

La interfaz de línea de comandos de Cobra puede personalizarse mediante un archivo de configuración.

## Ruta del archivo

- **Nombre:** `cobra-cli.toml`
- **Ubicación:** directorio de trabajo desde el que se ejecuta `cobra`.

## Claves soportadas

| Clave            | Valor por defecto                                    | Descripción                                           |
|------------------|------------------------------------------------------|-------------------------------------------------------|
| `language`       | `es`                                                 | Idioma de la interfaz de la CLI.                      |
| `default_command`| `interactive`                                       | Subcomando ejecutado si no se especifica otro.        |
| `log_format`     | `%(asctime)s - %(levelname)s - %(message)s`          | Formato para los mensajes de registro (*logging*).    |
| `program_name`   | `cobra`                                              | Nombre con el que aparece la aplicación en la ayuda.  |

Las variables de entorno `COBRA_LANG`, `COBRA_DEFAULT_COMMAND`, `COBRA_LOG_FORMAT` y `COBRA_PROGRAM_NAME` permiten sobrescribir estos valores.

## Política de seguridad para `SQLITE_DB_KEY` en la CLI

Para comandos que requieren base de datos (`cache`, `compilar`, `benchtranspilers`,
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

cobra compilar ejemplo.co --tipo python
```

#### Opción B (solo dev local): clave efímera por ejecución

```bash
COBRA_DEV_MODE=1 \
COBRA_DEV_ALLOW_EPHEMERAL_KEY=1 \
cobra --dev-ephemeral-key compilar ejemplo.co --tipo python
```

> Nota: evita esta opción en CI/prod; está diseñada únicamente para sesiones
> locales temporales.

## Ejemplo

```toml
# cobra-cli.toml
language = "en"
default_command = "compile"
log_format = "%(levelname)s: %(message)s"
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
wasm = "build/modulo.wasm"
go = "build/modulo.go"
cpp = "build/modulo.cpp"
java = "build/modulo.java"
asm = "build/modulo.asm"
```

### Reglas de validación

- Solo se aceptan nombres canónicos contenidos en `OFFICIAL_TARGETS`:
  `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java` y `asm`.
- Los aliases legacy, abreviaturas históricas y traducciones antiguas de nombres de backend no son válidos; usa siempre los 8 identificadores canónicos oficiales.
- Los mappings de módulos deben vivir dentro de `[modulos."..."]`; las estructuras en raíz ya no se resuelven.
- `cobra.mod` sigue siendo el archivo validado por `modulos`/empaquetado, pero sus backends también deben respetar exclusivamente los 8 nombres oficiales.

### ¿Qué targets pueden omitirse intencionalmente?

- Puedes omitir cualquier target **no incluido** en `required_targets`.
- Si no declaras política, la validación asume por defecto el Tier 1 completo:
  `python`, `rust`, `javascript` y `wasm`.
- Para proyectos que solo distribuyen un subconjunto de backends, ajusta
  explícitamente `required_targets` para evitar errores de validación.

## Política de targets oficial

La CLI no debe mantener listas duplicadas de lenguajes soportados. La fuente de
verdad para los targets oficiales es `src/pcobra/cobra/config/transpile_targets.py`
a través de `TARGETS_BY_TIER`, `TIER1_TARGETS`, `TIER2_TARGETS` y `OFFICIAL_TARGETS`. La
documentación pública y los archivos de configuración deben usar únicamente los
nombres canónicos `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`, `java` y
`asm`.

En consecuencia:

- `cobra compilar` debe derivar `TRANSPILERS` y `LANG_CHOICES` desde
  `OFFICIAL_TARGETS` y un registro canónico compartido.
- Los scripts auxiliares, especialmente benchmarks y validaciones CI, deben
  reutilizar utilidades comunes basadas en esa misma política.
- Cualquier nuevo backend oficial requiere actualizar primero esa fuente única y
  después el registro canónico correspondiente; no se permiten listas
  hardcodeadas duplicadas en la CLI o en scripts.
