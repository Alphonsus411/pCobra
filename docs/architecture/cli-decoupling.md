# CLI decoupling: reglas de acoplamiento entre comandos

Esta guía define la frontera de dependencias en `src/pcobra/cobra/cli/commands`.

## Regla principal

Dentro de `pcobra.cobra.cli.commands`, **ningún comando puede importar otro módulo de comandos**.

- ✅ Permitido: imports desde `pcobra.cobra.cli.commands.base`.
- ❌ Prohibido: imports desde cualquier otro módulo bajo `pcobra.cobra.cli.commands.*`.

Ejemplos:

```python
# ✅ permitido
from pcobra.cobra.cli.commands.base import BaseCommand, CommandError

# ❌ prohibido
from pcobra.cobra.cli.commands.compile_cmd import CompileCommand
from pcobra.cobra.cli.commands.helpers import helper
from .compile_cmd import CompileCommand
```

## ¿Por qué existe esta regla?

1. Evita acoplamiento horizontal entre comandos concretos.
2. Reduce ciclos de import y efectos secundarios al cargar CLI.
3. Obliga a compartir contrato común vía `commands.base` y servicios/utilidades del CLI.

## Cómo se valida

La regla se valida con el linter de CI:

```bash
python scripts/ci/lint_no_cross_command_imports.py
```

Si detecta imports cruzados, CI falla y reporta archivo + línea.
