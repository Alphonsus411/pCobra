# Guía básica de nuevos tokens

El lenguaje ahora reconoce dos palabras clave adicionales:

- `metodo`: puede utilizarse dentro de una `clase` como alternativa a `func` para definir métodos.
- `atributo`: permite acceder o asignar atributos de objetos.

Ejemplo de uso:

```cobra
clase Persona:
    metodo set_nombre(self, nombre):
        atributo self nombre = nombre
    metodo saludar(self):
        imprimir atributo self nombre
    fin
fin
```

## API de la biblioteca estándar

La carpeta `standard_library` agrupa utilidades listas para usarse desde Cobra.

### archivo

- `leer(ruta)` - devuelve el contenido de un archivo de texto.
- `escribir(ruta, datos)` - crea o reemplaza un archivo con el texto dado.
- `adjuntar(ruta, datos)` - agrega información al final del archivo.
- `existe(ruta)` - indica si la ruta existe.

### fecha

- `hoy()` - obtiene la fecha y hora actual.
- `formatear(fecha, formato='%Y-%m-%d')` - formatea una fecha.
- `sumar_dias(fecha, dias)` - suma días a una fecha dada.

### lista

- `cabeza(lista)` - primer elemento o `None` si está vacía.
- `cola(lista)` - lista sin el primer elemento.
- `longitud(lista)` - cantidad de elementos.
- `combinar(*listas)` - concatena varias listas.

### logica

- `conjuncion(a, b)` - equivalente a `a and b`.
- `disyuncion(a, b)` - equivalente a `a or b`.
- `negacion(a)` - equivalente a `not a`.

### util

- `es_nulo(valor)` - retorna `True` si es `None`.
- `es_vacio(secuencia)` - `True` si la secuencia está vacía.
- `repetir(cadena, veces)` - repite la cadena.
