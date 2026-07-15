# AGENTS.md — pCobra

Alcance: todo el repositorio.

## Reglas obligatorias para agentes

- No modificar Lexer ni Parser salvo autorización explícita y específica.
- No añadir tokens, palabras reservadas, reglas gramaticales, aliases ni sintaxis Cobra inventada.
- `docs/LIBRO_PROGRAMACION_COBRA.md` es la fuente normativa para sintaxis y comportamiento del lenguaje.
- Resolver hallazgos de auditoría de forma incremental, uno por uno, sin mezclar problemas.
- Hacer cambios mínimos y relacionados directamente con el hallazgo tratado.
- No cambiar ejemplos ni documentación para ocultar fallos de ejecución.
- No eliminar pruebas fallidas ni reducir aserciones para hacerlas pasar.
- Preservar compatibilidad de interfaces públicas cuando sea posible.
- Para runtime, preferir corregir intérprete, sandbox, servicios o aislamiento de procesos antes que cambiar sintaxis.
- Cuando un hallazgo no pueda resolverse sin tocar Lexer o Parser, detenerse y documentar el bloqueo.

## Verificaciones recomendadas

- Ejecutar primero pruebas dirigidas del hallazgo.
- Ejecutar después suites relacionadas.
- Verificar explícitamente que Lexer y Parser no cambiaron antes de finalizar.
- Revisar `git diff --check` y el diff final para detectar cambios accidentales.
