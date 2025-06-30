# Guía básica de Cobra

Este documento presenta un recorrido introductorio por el lenguaje Cobra con veinte ejemplos sencillos.

## 1. Hola mundo
```cobra
imprimir "Hola mundo"
```

## 2. Variables y operaciones
```cobra
x = 5
y = 3
imprimir x + y
```

## 3. Condicionales
```cobra
si x > y:
    imprimir "x es mayor"
sino:
    imprimir "y es mayor"
fin
```

## 4. Bucle mientras
```cobra
contador = 0
mientras contador < 3:
    imprimir contador
    contador = contador + 1
fin
```

## 5. Bucle para
```cobra
para i en [1, 2, 3]:
    imprimir i
fin
```

## 6. Funciones
```cobra
func cuadrado(n):
    regresar n * n
fin
imprimir cuadrado(4)
```

## 7. Listas
```cobra
numeros = [1, 2, 3]
imprimir longitud(numeros)
```

## 8. Diccionarios
```cobra
mapa = {"a": 1, "b": 2}
imprimir mapa["a"]
```

## 9. Lectura de archivos
```cobra
from archivo importar leer
contenido = leer("ejemplo.txt")
imprimir contenido
```

## 10. Escritura de archivos
```cobra
from archivo importar escribir
escribir("salida.txt", "datos")
```

## 11. Definición de clases
```cobra
clase Persona:
    metodo __init__(self, nombre):
        atributo self nombre = nombre
fin
```

## 12. Creación de objetos
```cobra
p = Persona("Eva")
```

## 13. Uso de `metodo`
```cobra
clase Animal:
    metodo sonido(self):
        imprimir "???"
    fin
fin
```

## 14. Uso de `atributo`
```cobra
p = Persona("Luis")
imprimir atributo p nombre
```

## 15. Importar módulos
```cobra
importar fecha
imprimir fecha.hoy()
```

## 16. Manejo de errores
```cobra
intentar:
    abrir("no_existe.txt")
excepto ErrorComoE:
    imprimir "fallo"
fin
```

## 17. Expresiones lógicas
```cobra
imprimir conjuncion(True, False)
```

## 18. Comprensión de listas
```cobra
cuadrados = [x * x para x en [1,2,3]]
```

## 19. Uso de la API `util`
```cobra
from util importar es_vacio
imprimir es_vacio([])
```

## 20. Programa principal
```cobra
func principal():
    imprimir "Listo"
fin
```
