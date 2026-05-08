# Revisión de cobertura frente a capacidades base de Python

## numero
- Cobertura previa sólida en métricas y teoría de números, pero faltaban en API pública algunos equivalentes de `math`/`statistics`: `raiz`, `potencia`, `mediana`, `moda`, `promedio`, `es_par`, `es_primo`, `factorial`.
- Se añadieron funciones públicas en español en `standard_library/numero.py` para cubrir esos faltantes.

## texto
- Ya cubre la mayor parte de operaciones base de `str` (búsqueda, partición, formato, normalización, traducción, predicados Unicode).
- No se agregaron funciones nuevas en esta iteración para evitar ampliar superficie sin necesidad funcional inmediata.

## datos
- Módulo orientado a tablas y estructuras; no busca replicar `list`/`dict` completos sino ofrecer operaciones de alto nivel (filtrado, mapeo, pivote, agregación).
- Sin faltantes críticos frente al objetivo del dominio Cobra.

## logica
- Cobertura adecuada para operadores booleanos y combinadores lógicos (`conjuncion`, `disyuncion`, `xor`, `implica`, `tabla_verdad`).
- Sin faltantes críticos detectados.

## asincrono
- Existía función delegada `recolectar` sin inclusión explícita en `__all__`, por lo tanto no era API pública estricta.
- Se añadió a `__all__` para alinear con patrón `asyncio.gather` en semántica Cobra.

## sistema
- Cobertura enfocada en ejecución segura de comandos y entorno; acorde al alcance de seguridad del runtime Cobra.

## archivo
- Cobertura suficiente para I/O de texto con sandbox de rutas; no se ampliaron capacidades para mantener política de seguridad.

## tiempo
- La fachada tenía inconsistencia de import interno; se corrigió para exponer correctamente API temporal base (`ahora`, `formatear`, `dormir`, `epoch`, `desde_epoch`).

## red
- La fachada tenía inconsistencia de import interno y faltaba publicar `obtener_url_texto` en `__all__`.
- Se corrigieron ambas cosas sin introducir alias backend.

## holobit
- Cobertura estable y especializada de dominio. Sin faltantes frente al alcance de este módulo.
