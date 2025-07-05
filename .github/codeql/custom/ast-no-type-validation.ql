import python

/**
 * Reporta clases que representan nodos de AST cuyo nombre
 * empieza por "Nodo" y cuyo método __post_init__ no contiene
 * validación de tipos mediante llamadas a `isinstance` ni
 * sentencias `assert`.
 */
from Class c
where
  c.getName().regexp("^Nodo") and
  not exists(Method m |
    m.getDeclaringType() = c and
    m.getName() = "__post_init__" and
    (
      // Búsqueda de llamada a builtin isinstance
      exists(FunctionCall fc |
        fc.getEnclosingCallable() = m and
        fc.getTarget().hasQualifiedName("isinstance")
      ) or
      // Búsqueda de sentencia assert
      exists(AssertStmt ast |
        ast.getEnclosingCallable() = m
      )
    )
  )
select c, "El nodo del AST carece de validación de tipos"
