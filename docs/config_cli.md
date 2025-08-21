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
program_name = "pcobra"
```

Otro ejemplo mínimo:

```toml
language = "es"
program_name = "cobra-cli"
```
