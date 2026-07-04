# `standard_library.cripto`

## Propósito

`cripto` agrupa ayudantes criptográficos básicos para calcular resúmenes, generar tokens y comparar secretos reduciendo filtraciones triviales por temporización.

## Funciones públicas

- `sha256(datos)`: calcula el resumen SHA-256.
- `sha512(datos)`: calcula el resumen SHA-512.
- `comparar_seguro(a, b)`: compara secretos con una rutina resistente a diferencias de tiempo simples.
- `token_seguro(tamano=32)`: genera bytes o texto aleatorio seguro según la implementación del runtime.
- `token_hexadecimal(tamano=32)`: genera un token hexadecimal seguro.

## Ejemplo mínimo

```cobra
usar "cripto"

token = cripto.token_hexadecimal(16)
resumen = cripto.sha256("mensaje")
si cripto.comparar_seguro(resumen, cripto.sha256("mensaje")):
    imprimir(token)
```

## Notas de error y degradación segura

- Los tamaños de token deben ser positivos; valores inválidos deben rechazarse de forma explícita.
- No usar estas funciones como sustituto de protocolos criptográficos completos; para cifrado, firmas o gestión de claves se requiere una biblioteca especializada.
