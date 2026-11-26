# F1 — Plan de intervención correctiva

Fecha: 2026-11-26. Autorización del propietario para desbloquear F1 mediante implementación aislada, con documentación previa. No autoriza merge ni publicación definitiva.

Base inmutable: `68e0465d3793078f2c7763f1e51f7748eb8e9f60`. Referencia histórica candidata: `08820d6c3426d71359911006c76a6a7fb260cfa0`. PR #3876 y #3877 permanecen independientes y en borrador.

## Alcance y secuencia

1. Documentar y crear rama aislada desde master.
2. Revisar runner, contrato de backend_pipeline y política canónica; sustituir invocación legacy compilar por mecanismo vigente, sin modificar semántica del lenguaje.
3. Exigir ejecución exitosa, stdout esperado 1001, timeout, limpieza y pico RSS individual; no admitir mediciones ausentes, no positivas o no finitas.
4. Exigir exactamente una medición de cada backend oficial en ambos conjuntos; obtener política de la fuente canónica; conservar umbral de regresión del 10 %.
5. Añadir pruebas focales de errores, conjuntos vacíos, parciales, extras, duplicados y métricas inválidas, manteniendo pruebas existentes.
6. Diseñar workflow independiente con permisos mínimos de lectura para medir referencia y candidato con instrumento común, mismos runtimes y carga; registrar SHA, entorno, versiones, muestras, hashes, salida y dispersión. No activar publicación automática. Validar procedencia de los programas generados.
7. Ejecutar captura real solo tras verificar workflow y permisos; conservar artefactos diagnósticos, no declarar baseline oficial sin aprobación humana.
8. Certificar comparación y CI solamente con evidencia completa, sin ocultar errores. Revisar diferencias antes de solicitar aprobación.

## Restricciones

No modificar master, fusionar PR, publicar release o baseline definitivo, ampliar backends (Python, JavaScript, Rust), relajar umbral, fabricar métricas, introducir continue-on-error ni tocar lexer, parser, AST, gramática o semántica. Limitar cambios a scripts de benchmarks, pruebas focales, documentación y workflow específico. Cualquier cambio adicional requiere revisión de alcance previa. Los artefactos históricos vacíos o metodológicamente incompatibles no son referencias válidas.

## Aceptación y reversión

Tres backends ejecutados correctamente en ambos commits, salida funcional 1001, mediciones reales trazables y positivas, pruebas originales y adicionales satisfechas, comparación contra referencia compatible, job satisfactorio y revisión humana. Mantener commits pequeños y reversibles; abandonar rama o revertir commits individuales únicamente con autorización; master permanece intacto. F1.13 y F1.14 siguen pendientes hasta contar con evidencia real.
