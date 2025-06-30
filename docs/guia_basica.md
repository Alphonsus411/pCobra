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
