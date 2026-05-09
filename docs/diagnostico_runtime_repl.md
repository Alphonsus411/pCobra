# Diagnóstico de runtime REPL (`PCOBRA_DEBUG_RUNTIME`)

Este diagnóstico está **desactivado por defecto**.

## Activación

En Linux/macOS:

```bash
PCOBRA_DEBUG_RUNTIME=1 cobra repl
```

En Windows (PowerShell):

```powershell
$env:PCOBRA_DEBUG_RUNTIME = "1"
cobra repl
```

## Qué registra

Cuando `PCOBRA_DEBUG_RUNTIME=1`:

1. En el entrypoint del REPL se registra:
   - la ruta del archivo Python (`__file__`) de la clase concreta del intérprete activo,
   - la clase concreta que ejecuta la evaluación de llamadas de función.
2. En `ejecutar_usar` se registra la lista de símbolos inyectados **solo por nombre** luego de sanitización.

## Privacidad y alcance

- No se exponen objetos internos ni contenido privado de backend.
- El log de `usar` incluye únicamente nombres sanitizados de exportación pública.
- Si el flag no está activo, no se emiten estos logs adicionales.
