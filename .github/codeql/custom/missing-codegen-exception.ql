import python

/**
 * Reporta métodos "generate_code" en los transpiladores que no contienen
 * sentencias try/except para manejar excepciones durante la generación de código.
 */
from Method m, File f
where
  m.getName() = "generate_code" and
  m.getFile() = f and
  f.getRelativePath().regexp("^backend/src/cobra/transpilers/transpiler/") and
  not exists(TryStmt t |
    t.getEnclosingCallable() = m
  )
select m, "Falta manejo de excepciones durante la generación de código"
