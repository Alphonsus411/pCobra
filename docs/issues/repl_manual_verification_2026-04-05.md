# Verificación manual REPL (2026-04-05)

Se validó el comportamiento del REPL con una ejecución interactiva controlada usando `InteractiveCommand._run_repl_loop` y entradas secuenciales simuladas (equivalentes a escribir en consola).

Comando usado:

```bash
python - <<'PY'
from types import SimpleNamespace
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand

interp = InterpretadorCobra()
cmd = InteractiveCommand(interp)

lineas = iter([
    '5 == 5',
    '5 == 6',
    '42',
    'imprimir "hola"',
    'a = 10',
    'salir',
])

def leer(_prompt):
    try:
        linea = next(lineas)
        print(f'>> {linea}')
        return linea
    except StopIteration:
        raise EOFError

args = SimpleNamespace()
cmd._run_repl_loop(args=args, validador=None, leer_linea=leer, sandbox=False, sandbox_docker=None)
PY
```

## Resultados

1. `5 == 5` imprime `verdadero` ✅
2. `5 == 6` imprime `falso` ✅
3. Expresiones no booleanas:
   - Numérica (`42`) se imprime `42` sin formato adicional ✅
   - String mediante `imprimir "hola"` se imprime `hola` (sin formato extra del REPL) ✅
4. Los logs de depuración existentes siguen apareciendo (`[RUN]`, `[EXEC]`, también `[AST BEFORE OPT]`/`[AST AFTER OPT]`) ✅
5. En sentencias sin valor visible no hay impresión adicional del REPL:
   - `imprimir "hola"` no duplica salida (solo la propia instrucción)
   - El REPL solo imprime automáticamente cuando el resultado de ejecución no es `None` ✅

## Nota

En una ejecución TTY real con `prompt_toolkit` (`python -m pcobra interactive`), se reprodujo inestabilidad del loop asíncrono en este entorno al enviar una entrada con comillas simples. La validación funcional principal se completó con el loop interactivo canónico (`_run_repl_loop`).
