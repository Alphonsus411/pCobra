import python

/**
 * Reporta el uso de 'eval' o 'exec' fuera del sandbox.
 */
from Call c, File f
where
  exists(GlobalVariable builtin |
    builtin = c.getFunc().(Name).getVariable() and
    builtin.getId() in ["eval", "exec"]
  ) and
  f = c.getLocation().getFile() and
  f.getRelativePath().regexpMatch("^src/.*") and
  not f.getRelativePath().regexpMatch("^src/core/sandbox.py$")
select c, "Uso potencialmente inseguro de eval/exec"
