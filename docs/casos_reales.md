# Casos de uso históricos

> **Documento histórico — no es una guía ejecutable del contrato actual.**
>
> Los ejemplos archivados en `examples/casos_reales/` y
> `notebooks/casos_reales/` se conservan para trazabilidad. Fueron creados antes
> de la política pública vigente de módulos y pueden contener sintaxis, comandos
> o integraciones que pCobra ya no admite directamente.

## Qué no debe inferirse de estos ejemplos

- `usar` no importa paquetes Python como `sklearn`, `pandas`, `matplotlib`,
  `flask`, `pygame` o `biopython`.
- Instalar una dependencia externa no la convierte en un módulo Cobra.
- AGIX es el motor interno de sugerencias de la distribución Python; no es un
  módulo público accesible mediante `usar "analizador_agix"`.
- Un paquete instalado desde CobraHub no amplía automáticamente el catálogo
  público de `usar`.
- Los comandos y rutas de compilación mostrados en cuadernos antiguos pueden
  pertenecer a flujos retirados.

## Contrato vigente

Para escribir código nuevo, utiliza únicamente estas referencias:

1. [Libro de Programación Cobra](LIBRO_PROGRAMACION_COBRA.md), ruta principal de
   aprendizaje.
2. [Manual de Cobra](MANUAL_COBRA.md), referencia técnica canónica.
3. [Especificación del lenguaje](SPEC_COBRA.md), gramática implementada.
4. [Inventario público de módulos de `usar`](inventario_usar_modulos.md).
5. [Manual de CobraHub](frontend/cobrahub.rst), para empaquetado y distribución
   de artefactos `.co`.

La forma canónica de una función nueva es:

```cobra
func saludar(nombre):
    retorno "Hola, " + nombre
fin
```

La forma canónica de cargar un módulo es:

```cobra
usar "texto"
usar "utilidades.fechas"
```

El primer ejemplo usa un módulo canónico. El segundo usa un archivo `.cobra`
local resuelto dentro de la raíz verificada del proyecto.

## Material archivado

Los siguientes directorios permanecen disponibles exclusivamente para estudio
histórico y migración:

- `examples/casos_reales/bioinformatica/`
- `examples/casos_reales/inteligencia_artificial/`
- `examples/casos_reales/analisis_datos/`
- `notebooks/casos_reales/`

Antes de reutilizar cualquiera de esos archivos, hay que migrarlo al contrato
vigente y validar el resultado con el Lexer, el Parser y la CLI actuales. No se
debe copiar su sintaxis ni sus imports a documentación nueva sin esa revisión.
