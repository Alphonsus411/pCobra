/**
 * Reporta métodos "generate_code" en los transpiladores que no contienen
 * sentencias try/except para manejar excepciones durante la generación de código.
 * @name Falta manejo de excepciones en generación de código
 * @description Detecta métodos generate_code sin sentencias try/except.
 * @kind problem
 * @problem.severity warning
 * @id py/missing-codegen-exception
 */

import python

from Function m, File f
where
  m.getName() = "generate_code" and
  m.getLocation().getFile() = f and
  f.getRelativePath().regexpMatch("^src/cobra/transpilers/transpiler/.*") and
  not exists(Try t |
    t.getScope() = m
  )
select m, "Falta manejo de excepciones durante la generación de código"
