# Manual del Lenguaje Cobra

Este manual presenta en español los conceptos básicos para programar en Cobra. Se organiza en tareas que puedes seguir paso a paso.

## 1. Preparación del entorno

1. Clona el repositorio y entra en el directorio `pCobra`.
2. Crea y activa un entorno virtual.
3. Instala las dependencias con `pip install -r requirements.txt`.
4. Instala la herramienta de forma editable con `pip install -e .`.

## 2. Estructura básica de un programa

- Declara variables con `var`.
- Define funciones con `func nombre(parametros) :` y finaliza con `fin` si la función es multilinea.
- Utiliza `imprimir` para mostrar datos en pantalla.

```cobra
var mensaje = 'Hola Mundo'
imprimir(mensaje)
```

## 3. Control de flujo

- Condicionales con `si`, `sino` y `fin` opcional.
- Bucles `mientras` y `para`.

```cobra
var x = 0
mientras x < 3 :
    imprimir(x)
    x += 1
```

## 4. Trabajar con módulos

- Usa `import` para cargar archivos `.cobra` o módulos nativos.
- Los módulos nativos ofrecen funciones de E/S y estructuras de datos.

```cobra
import 'modulo.cobra'
imprimir(saludo)
```

## 5. Concurrencia

- Ejecuta funciones en paralelo con la palabra clave `hilo`.

```cobra
func tarea():
    imprimir('trabajo')
fin

hilo tarea()
imprimir('principal')
```

## 6. Transpilación y ejecución

- Compila a Python o JavaScript con `cobra compilar archivo.cobra --tipo python`.
- Ejecuta directamente con `cobra ejecutar archivo.cobra`.

## 7. Modo seguro

- Añade `--seguro` para evitar operaciones peligrosas como `leer_archivo` o `hilo`.

```bash
cobra ejecutar programa.cobra --seguro
```

## 8. Próximos pasos

Revisa la documentación en `frontend/docs` para profundizar en la arquitectura, validadores y más ejemplos.
