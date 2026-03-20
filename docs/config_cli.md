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

## Mappings multi-backend (`cobra.toml` y `cobra.mod`)

Para resolver imports de módulos transpilados en varios backends, define rutas por
target en `cobra.mod` y opcionalmente declara la política de targets requeridos en
`pcobra.toml`/`cobra.toml`:

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

### ¿Qué targets pueden omitirse intencionalmente?

- Puedes omitir cualquier target **no incluido** en `required_targets`.
- Si no declaras política, la validación asume por defecto el Tier 1 completo:
  `python`, `rust`, `javascript` y `wasm`.
- Para proyectos que solo distribuyen un subconjunto de backends, ajusta
  explícitamente `required_targets` para evitar errores de validación.

## Política de targets oficial

La CLI no debe mantener listas duplicadas de lenguajes soportados. La fuente de
verdad para los targets oficiales es `src/pcobra/cobra/transpilers/targets.py`
a través de `TIER1_TARGETS`, `TIER2_TARGETS` y `OFFICIAL_TARGETS`. La
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
