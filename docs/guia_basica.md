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

## 21. Funciones asincrónicas
```cobra
asincronico func saluda():
    imprimir 1
fin

asincronico func principal():
    esperar saluda()
fin

esperar principal()
```

## 22. Decoradores
```cobra
@mi_decorador
func saluda():
    imprimir "Hola"
fin
```

## 23. Manejo de excepciones
```cobra
intentar:
    abrir("noexiste.txt")
capturar e:
    imprimir "Error:" + e
fin
```

## 24. Suma de matrices
```cobra
func sumar_matriz():
    var a11 = 1
    var a12 = 2
    var a21 = 3
    var a22 = 4

    var b11 = 5
    var b12 = 6
    var b21 = 7
    var b22 = 8

    imprimir a11 + b11
    imprimir a12 + b12
    imprimir a21 + b21
    imprimir a22 + b22
fin

sumar_matriz()
```

## 25. Factorial recursivo
```cobra
func factorial(n):
    si n <= 1:
        retorno 1
    sino:
        retorno n * factorial(n - 1)
    fin
fin

imprimir factorial(5)
```

## 26. Comando verify
El subcomando `cobra verificar` (`cobra verify`) comprueba que un programa
genere la misma salida en distintos lenguajes.
