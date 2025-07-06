# Clases

Este directorio contendrá ejemplos de programación orientada a objetos con
Cobra. Los archivos mostrarán cómo declarar clases, crear instancias y emplear
métodos y atributos.

## Archivos

- `persona.co` define la clase `Persona` con un método `saludar`.
- `estudiante.co` hereda de `Persona` y añade el método `presentar`.
- `main.co` crea instancias de `Estudiante` y ejecuta sus métodos.

## Compilación y ejecución

Para compilar cada archivo a Python y ejecutar `main.co` usa:

```bash
cobra compilar persona.co --tipo python > persona.py
cobra compilar estudiante.co --tipo python > estudiante.py
cobra compilar main.co --tipo python > main.py
python main.py
```
