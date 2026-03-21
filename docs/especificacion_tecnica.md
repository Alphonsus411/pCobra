# Especificación Técnica de Cobra

Este documento resume la sintaxis y la semántica básica del lenguaje Cobra.

Para ver ejemplos completos de compilación y transpilación, consulta la carpeta [`examples/hello_world`](../examples/hello_world), donde encontrarás un `README.md` con instrucciones de uso y los códigos generados para targets oficiales.

## Targets oficiales de transpilación

En runtime oficial y para soporte de producción, Cobra define **únicamente** 8
targets de transpilación: `python`, `rust`, `javascript`, `wasm`, `go`, `cpp`,
`java` y `asm`.

La fuente de verdad de este contrato es:
`src/pcobra/cobra/transpilers/targets.py` (`OFFICIAL_TARGETS`).

Cualquier backend o pipeline fuera de esa lista debe considerarse experimental y no forma
parte del paquete instalable de producción.

## Experimentos y documentación separada

Los materiales sobre Hololang, LLVM, reverse desde LaTeX o referencias retiradas de reverse no amplían la lista anterior. Tampoco deben enlazarse desde la documentación principal de forma ambigua o sin etiquetar su estado.

- **Hololang**: se documenta como IR interno y flujo auxiliar, no como target público de salida.
- **LLVM / LaTeX / reverse WASM retirado**: se mantienen separados en `docs/experimental/` y deben citarse como `experimental` o `fuera de política`.
- **Histórico**: los documentos archivados deben permanecer en `docs/historico/` y citarse como `histórico` o `sin vigencia normativa`.

## Estructura general

Un programa Cobra está formado por sentencias separadas por saltos de línea e indentadas con espacios. El punto de entrada se define en la función `principal`.

## Comentarios

Se indican con el carácter `#` y se extienden hasta el final de la línea.

```cobra
# Esto es un comentario
```

## Variables y tipos

Las variables se asignan con `=`. Cobra soporta números, cadenas, listas y diccionarios.

```cobra
x = 10
nombre = "Ana"
lista = [1, 2, 3]
mapa = {"a": 1, "b": 2}
```

## Funciones

Las funciones se definen con `func` y pueden devolver valores con `regresar`.

```cobra
func sumar(a, b):
    regresar a + b
fin
```

## Clases y objetos

Las clases utilizan la palabra `clase`. Los métodos se declaran con `metodo`.

```cobra
clase Persona:
    metodo __init__(self, nombre):
        atributo self nombre = nombre
    metodo saludar(self):
        imprimir "Hola", atributo self nombre
    fin
fin
```

Las clases pueden heredar de varias bases listándolas entre paréntesis. La búsqueda de métodos se realiza de izquierda a derecha.

```cobra
clase Mezcla(Base1, Base2):
    fin
```

Cuando una clase está precedida por `@registro`, Cobra genera automáticamente
los métodos `__init__/constructor`, `__repr__/toString` y `__eq__/equals`
utilizando los campos declarados en el cuerpo como atributos de instancia. Los
valores asignados se convierten en parámetros opcionales en el constructor.

## Control de flujo

Cobra cuenta con condicionales `si`, `sino` y bucles `para` y `mientras`.

```cobra
si x > 0:
    imprimir "positivo"
sino:
    imprimir "no positivo"
fin
```

## Módulos

Los archivos pueden importarse usando `import`.

```cobra
import utilidades
```

## Manejo de errores

El bloque `intentar` ... `capturar` captura excepciones y puede incluir `finalmente`.

```cobra
intentar:
    ejecutar_algo()
capturar e:
    imprimir(e)
fin
```

## Semántica

Cobra evalúa expresiones de izquierda a derecha. Los parámetros se pasan por valor. El ámbito de las variables es estático, determinado por la indentación.

## Decoradores

Los decoradores se indican con `@` y permiten modificar funciones antes de su ejecución.

```cobra
@medir_tiempo
func tarea():
    imprimir "hola"
fin
```

## Funciones lambda

Las lambdas son funciones anónimas de una sola expresión.

```cobra
doble = lambda x: x * 2
```

## Gestión de contextos

El bloque `con` gestiona contextos y cierra recursos automáticamente.

```cobra
con archivo("datos.txt") como f:
    imprimir(f.leer())
fin
```

## Asincronía

Las funciones pueden marcarse como `asincronico` y utilizar `esperar` para suspender su ejecución hasta que otra operación termine.

```cobra
asincronico func descargar():
    datos = esperar solicitar()
    retornar datos
fin
```

## Option

La construcción `option` declara valores opcionales que pueden o no contener un dato.

```cobra
option resultado = obtener()
option sin_valor = None
```

## Switch ampliado

`switch` admite múltiples valores por caso y un bloque `default` opcional.

```cobra
switch x:
    case 1, 2:
        imprimir "uno o dos"
    default:
        imprimir "otro"
fin
```

## Almacenamiento y migración de la caché

La caché incremental de tokens y AST se gestiona mediante SQLitePlus. Por defecto
se crea la base `~/.cobra/sqliteplus/core.db`, accesible únicamente si se define
la variable de entorno `SQLITE_DB_KEY`. Para usar otra ubicación establece
`COBRA_DB_PATH` antes de ejecutar la CLI o los módulos de análisis.

Las instalaciones con archivos JSON generados por versiones anteriores pueden
migrarse con:

```bash
python scripts/migrar_cache_sqliteplus.py --origen /ruta/a/cache
```

Este script recorre los hashes guardados en `.ast`/`.tok`, los inserta en la base
de datos y deja el entorno listo para reutilizar la caché desde la nueva
infraestructura.
