# Guía básica de Cobra (resumen rápido)

> **Estado del documento: Histórico**
>
> Este archivo se mantiene como resumen de consulta rápida (1 página). La ruta pedagógica completa vive en el [Libro de Programación con Cobra](LIBRO_PROGRAMACION_COBRA.md).

## ¿Qué leer según tu objetivo?

- **Aprender Cobra de cero a avanzado**: [Libro de Programación con Cobra](LIBRO_PROGRAMACION_COBRA.md)
- **Consultar sintaxis/contrato técnico**: [Manual de Cobra (referencia)](MANUAL_COBRA.md)
- **Referencia en formato RST**: [MANUAL_COBRA.rst](MANUAL_COBRA.rst)

## Inicio en 5 minutos

1. Instala dependencias:

```bash
python -m venv .venv
source .venv/bin/activate  # Unix
# .\.venv\Scripts\activate  # Windows PowerShell
./scripts/install_dev.sh
pip install -e .
```

2. Crea `hola.co`:

```cobra
imprimir("Hola, Cobra")
```

3. Ejecuta:

```bash
cobra run hola.co
```

## Mini mapa del lenguaje

```cobra
# Variables
nombre = "Ada"

# Condicional
si nombre == "Ada":
    imprimir("Bienvenida")

# Bucle
para n en [1, 2, 3]:
    imprimir(n)

# Función
funcion cuadrado(x):
    retornar x * x
```

## Enlaces directos al libro

- Fundamentos: [2. Primeros pasos](LIBRO_PROGRAMACION_COBRA.md#2-primeros-pasos)
- Sintaxis: [3. Sintaxis base](LIBRO_PROGRAMACION_COBRA.md#3-sintaxis-base-del-lenguaje)
- Flujo de control: [4. Control de flujo](LIBRO_PROGRAMACION_COBRA.md#4-control-de-flujo)
- Funciones: [5. Funciones y reutilización](LIBRO_PROGRAMACION_COBRA.md#5-funciones-y-reutilización)
- Estructuras de datos: [6. Estructuras de datos](LIBRO_PROGRAMACION_COBRA.md#6-estructuras-de-datos)
- Módulos e imports: [7. Módulos, imports y organización](LIBRO_PROGRAMACION_COBRA.md#7-módulos-imports-y-organización-de-código)
- CLI diaria: [10. CLI de Cobra](LIBRO_PROGRAMACION_COBRA.md#10-cli-de-cobra-para-desarrollo-diario)
- Targets y compatibilidad: [11. Transpilación, targets y compatibilidad](LIBRO_PROGRAMACION_COBRA.md#11-transpilación-targets-y-compatibilidad)

## Nota de mantenimiento

Este documento evita repetir tutoriales extensos. Para contenido didáctico detallado y actualizado, prioriza siempre el libro principal.
