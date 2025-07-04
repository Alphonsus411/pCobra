Patrones de diseño en Cobra
==========================

Visitor Pattern
---------------

En el módulo ``src.core`` se utiliza el patrón *Visitor* para procesar el
árbol de sintaxis abstracta (AST). Todos los nodos heredan de
``NodoAST`` y exponen el método ``aceptar`` que delega la operación en una
instancia de ``NodeVisitor``.

.. code-block:: python

   @dataclass
   class NodoAST:
       """Clase base para todos los nodos del AST."""

       def aceptar(self, visitante):
           """Acepta un visitante y delega la operación a éste."""
           return visitante.visit(self)

``NodeVisitor`` se encarga de despachar al método ``visit_<nodo>``
correspondiente según el tipo de cada nodo:

.. code-block:: python

   class NodeVisitor:
       """Recorre nodos del AST despachando al método adecuado."""

       def visit(self, node):
           method_name = f"visit_{self._camel_to_snake(node.__class__.__name__)}"
           visitor = getattr(self, method_name, self.generic_visit)
           return visitor(node)

Un visitante personalizado sólo necesita implementar los métodos que
requiera:

.. code-block:: python

   class MiVisitor(NodeVisitor):
       def visit_asignacion(self, nodo):
           print("Asignando a", nodo.variable)

   n = NodoAsignacion("x", NodoValor(1))
   n.aceptar(MiVisitor())

Fábrica de transpiladores
------------------------

El comando ``compilar`` utiliza un diccionario ``TRANSPILERS`` como
fábrica de transpiladores. Cada entrada asocia un alias con la clase que
implementa la conversión de AST a un lenguaje concreto.
Los transpiladores externos se registran a través de *entry points* y se
agregan al diccionario al iniciar el comando.

.. code-block:: python

   TRANSPILERS = {
       "python": TranspiladorPython,
       "js": TranspiladorJavaScript,
       ...
   }

   for ep in entry_points(group="cobra.transpilers"):
       module_name, class_name = ep.value.split(":", 1)
       cls = getattr(import_module(module_name), class_name)
       TRANSPILERS[ep.name] = cls

Cuando se solicita un lenguaje, se instancia la clase correspondiente y se
llama a ``transpilar`` sobre el AST:

.. code-block:: python

   transp = TRANSPILERS[lang]()
   codigo = transp.transpilar(ast)

Cada transpilador hereda de ``NodeVisitor`` e inyecta las funciones de
visita desde módulos específicos. Por ejemplo, en el backend de Go se
asignan dinámicamente las funciones ``visit_<nodo>``:

.. code-block:: python
   :emphasize-lines: 12-13

   # Asignar visitantes
   for nombre, funcion in go_nodes.items():
       setattr(TranspiladorGo, f"visit_{nombre}", funcion)

Otros lenguajes como C++ realizan asignaciones equivalentes de forma
explícita para mantener separada la lógica de cada nodo.
