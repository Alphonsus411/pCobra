# Contrato mínimo de runtime Holobit

## Objetivo

Definir una API mínima y estable para que los transpiladores de Cobra soporten los nodos Holobit de forma homogénea entre backends.

## Nombres canónicos

El runtime Holobit mínimo expone **4 hooks**:

1. `cobra_holobit(valores)`
2. `cobra_proyectar(hb, modo)`
3. `cobra_transformar(hb, op, ...params)`
4. `cobra_graficar(hb)`

> Nota: la forma exacta de la firma varía por lenguaje destino (por ejemplo, `...params` en JS/Go/Java, slices en Rust, listas en C++), pero la **semántica debe preservarse**.

## Semántica mínima

### `cobra_holobit(valores)`
- **Entrada**: colección indexable de valores numéricos.
- **Salida**: representación runtime del holobit para el backend.
- **Comportamiento mínimo**: si no hay tipo Holobit nativo, devolver/retener la colección de entrada.

### `cobra_proyectar(hb, modo)`
- **Entrada**: un holobit `hb` y descriptor de modo `modo`.
- **Salida**: resultado de la proyección o `hb` cuando aplica fallback.
- **Comportamiento mínimo**: delegar en implementación nativa si existe; en fallback registrar traza y no fallar por ausencia de backend avanzado.

### `cobra_transformar(hb, op, ...params)`
- **Entrada**: holobit `hb`, operación `op`, parámetros opcionales.
- **Salida**: holobit transformado o `hb` sin cambios en fallback.
- **Comportamiento mínimo**: aplicar operación cuando el backend la soporte; en caso contrario, trazar y continuar.

### `cobra_graficar(hb)`
- **Entrada**: holobit `hb`.
- **Salida**: backend-dependent (visualización, texto, no-op con traza).
- **Comportamiento mínimo**: no abortar ejecución si solo existe salida degradada.

## Política de inserción de hooks

Los transpiladores solo deben insertar hooks/imports de runtime Holobit cuando el AST incluya nodos:
- `NodoHolobit`
- `NodoProyectar`
- `NodoTransformar`
- `NodoGraficar`

Si no aparecen estos nodos, no se inyecta runtime Holobit.

## Estado de implementación por backend

- Python, JavaScript, Rust, Go, C++, Java: hooks ejecutables (funciones/métodos invocables).
- WASM, ASM: hooks ejecutables mínimos (stubs no-op válidos para ensamblado/generación).
