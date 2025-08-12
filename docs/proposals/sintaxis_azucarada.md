# Propuesta de azúcar sintáctica para Cobra

## Antecedentes

La gramática actual utiliza delimitadores como `:` y `fin` para cerrar bloques y repite palabras clave completas en varias construcciones. Esto puede resultar verboso, especialmente en definiciones de funciones, estructuras de control y condicionales.

## Azúcar sintáctica sugerida

### Bloques con llaves
En lugar de `func nombre(): ... fin`, permitir `func nombre() { ... }`.

```cobra
func saludar() {
    imprimir("hola")
}
```

### Funciones de expresión
Permitir abreviatura de funciones que retornan una única expresión.

```cobra
func doble(x) => x * 2
```

### Condicionales encadenados
Simplificar `si/si no` repetitivos con `sino si`.

```cobra
si x > 10 {
    imprimir("alto")
} sino si x > 5 {
    imprimir("medio")
} sino {
    imprimir("bajo")
}
```

## Implicaciones

- **Parser**: la gramática debe aceptar llaves y la forma abreviada `=>` en las reglas de `funcion`, `bucle_para` y `condicional`. También se requerirán reglas para `sino si`.
- **AST** (`src/core/ast_nodes.py`): se pueden reutilizar nodos existentes como `NodoFuncion` y `NodoCondicional`, pero será necesario detectar variantes abreviadas y posiblemente añadir banderas para distinguir cuerpos con llaves y funciones de expresión.

