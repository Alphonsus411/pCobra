# Propuesta de nuevos tipos para Cobra

## Antecedentes

La revisión de `src/core/type_utils.py` revela que la verificación de tipos se
limita a números, cadenas y booleanos. La `standard_library` ofrece utilidades
básicas pero carece de estructuras de datos avanzadas y abstracciones para el
manejo seguro de valores.

## Tipos propuestos

### Mapa
Colección de pares clave-valor con claves únicas. Permite acceso y actualización
rápida por clave.

### Conjunto
Estructura que almacena elementos únicos sin orden específico. Útil para
operaciones de pertenencia y diferencias.

### Registro
Tipo compuesto que agrupa campos con nombre. Facilita la creación de objetos
ligeros sin lógica asociada.

### Opción
Representa la presencia (`Algun`) o ausencia (`Nada`) de un valor. Evita
referencias nulas explícitas.

### Resultado
Encapsula el resultado de una operación que puede fallar, con variantes `Ok` y
`Error`. Propicia un manejo de errores expresivo.

### Decimal
Tipo numérico de precisión arbitraria para cálculos financieros.

## Priorización

1. **Mapa** – Alto impacto, implementación factible usando `dict` de Python.
2. **Conjunto** – Alto impacto, se puede basar en `set` nativo.
3. **Opción** – Medio impacto, requiere soporte de tipado opcional.
4. **Resultado** – Medio impacto, demanda convenciones para propagación de
   errores.
5. **Registro** – Bajo impacto inicial, pero útil para estructurar datos.
6. **Decimal** – Bajo impacto, depende de módulo `decimal`.
