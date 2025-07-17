---
name: Solicitud de mejora
about: Sugiere una nueva función o mejora
title: "[Mejora] Cache de AST con checksum"
labels: [enhancement, avanzado]
assignees: ''
---

**¿Tu solicitud está relacionada con un problema? Por favor descríbelo.**

La recompilación de archivos grandes es costosa incluso cuando no han cambiado.

**Describe la solución que te gustaría**

Guardar un hash del AST generado y reutilizarlo cuando el código fuente no se haya modificado.

**Alternativas consideradas**

Usar herramientas externas de cacheo como ccache, aunque no están diseñadas para AST.

**Contexto adicional**

El hito está mencionado en `ROADMAP.md` dentro de la versión 1.3.
