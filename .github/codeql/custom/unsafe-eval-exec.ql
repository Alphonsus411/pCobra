import python

/**
 * Reporta el uso de 'eval' o 'exec' fuera del sandbox.
 */
from Call c, File f
where
  (
    c.getTarget().hasQualifiedName("builtins", "eval") or
    c.getTarget().hasQualifiedName("builtins", "exec")
  ) and
  f = c.getFile() and
  f.getRelativePath().regexp("^backend/src/") and
  not f.getRelativePath().regexp("^backend/src/core/sandbox.py$")
select c, "Uso potencialmente inseguro de eval/exec"
