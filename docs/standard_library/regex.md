# `standard_library.regex`

## Propósito

`regex` expone operaciones frecuentes con expresiones regulares para buscar, validar, reemplazar, dividir y enumerar coincidencias en texto.

## Funciones públicas

- `buscar(patron, texto)`: busca la primera coincidencia.
- `coincidir(patron, texto)`: comprueba coincidencia desde el inicio del texto.
- `reemplazar(patron, sustituto, texto)`: reemplaza coincidencias.
- `dividir(patron, texto)`: divide texto usando un patrón.
- `encontrar_todos(patron, texto)`: devuelve todas las coincidencias.

## Ejemplo mínimo

```cobra
usar "regex"

si regex.coincidir("^[a-z]+$", "cobra"):
    palabras = regex.encontrar_todos("[a-z]+", "cobra lang")
    imprimir(palabras)
```

## Notas de error y degradación segura

- Patrones inválidos deben traducirse a errores claros, no a fallos silenciosos.
- Evitar patrones de complejidad excesiva con entradas no confiables para reducir riesgos de consumo elevado de CPU.
