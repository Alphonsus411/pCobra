/**
 * @name Nodo AST sin validación de tipos
 * @description Reporta clases Nodo cuyo __post_init__ no valida tipos mediante isinstance o assert.
 * @kind problem
 * @problem.severity error
 * @precision high
 * @id py/ast-no-type-validation
 * @tags security
 */

import python

from Class c
where
  c.getName().regexpMatch("^Nodo.*") and
  not exists(Function m |
    m.getScope() = c and
    m.getName() = "__post_init__" and
    (
      // Búsqueda de llamada a builtin isinstance
      exists(Call call |
        call.getScope() = m and
        call.getFunc().(Name).getId() = "isinstance"
      ) or
      // Búsqueda de sentencia assert
      exists(Assert ast |
        ast.getScope() = m
      )
    )
  )
select c, "El nodo del AST carece de validación de tipos"
