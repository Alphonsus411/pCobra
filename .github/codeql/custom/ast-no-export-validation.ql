/**
 * @name Exportación de AST sin validación
 * @description Detecta puntos de exportación de AST que no validan el árbol antes de devolverlo.
 * @kind problem
 * @problem.severity error
 * @precision high
 * @id py/ast-no-export-validation
 * @tags security
 */

import python

predicate isAstParseCall(Call call) {
  call.getFunc().(Name).getId() = "parse_source"
}

predicate isAstValidationCall(Call call) {
  call.getFunc().(Name).getId().regexpMatch("^(validate|validate_ast)$")
}

from Function exporter, Call parse
where
  exporter.getName() = "export_ast" and
  parse.getScope() = exporter and
  isAstParseCall(parse) and
  not exists(Call validation |
    validation.getScope() = exporter and
    isAstValidationCall(validation)
  )
select parse, "El AST se exporta sin validarlo."
