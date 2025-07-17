---
name: Solicitud de mejora
about: Sugiere una nueva función o mejora
title: "[Mejora] Transpilación multi-lenguaje en paralelo"
labels: [enhancement, avanzado]
assignees: ''
---

**¿Tu solicitud está relacionada con un problema? Por favor descríbelo.**

Al generar código para varios backends el proceso es secuencial y toma mucho tiempo.

**Describe la solución que te gustaría**

Ejecutar la transpilación a diferentes lenguajes en hilos o procesos independientes para reducir el tiempo total.

**Alternativas consideradas**

Mantener la transpilación secuencial y documentar cómo paralelizar manualmente.

**Contexto adicional**

Aprovechar el módulo `concurrent.futures` o bibliotecas de procesamiento paralelo.
