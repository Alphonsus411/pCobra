Arquitectura de Cobra
=====================

El proyecto se divide en distintos componentes que interactúan para
ofrecer una experiencia completa de desarrollo:

CLI
---
La interfaz de línea de comandos permite ejecutar programas Cobra,
compilar a otros lenguajes y gestionar módulos instalados.
Para ampliar estas funciones se emplea un sistema de plugins. Cada
plugin hereda de ``PluginCommand`` y se registra siguiendo el patrón
Command (ver :ref:`patron_command`).

Core
----
Contiene el corazón del lenguaje: lexer, parser, intérprete y
transpiladores a Python, JavaScript, ensamblador, Rust, C++, Go, R, Julia, Java, COBOL, Fortran, Pascal, Ruby, PHP, Matlab y LaTeX. Estos elementos trabajan en
conjunto para analizar el código fuente y transformarlo en otras
representaciones o ejecutarlo de forma directa.
Las clases que componen el AST se definen en ``src.core.ast_nodes`` para facilitar su reutilización.
El recorrido de estos nodos puede realizarse mediante la clase ``NodeVisitor``
ubicada en ``src.core.visitor``, que despacha automáticamente al método
``visit_<Clase>`` correspondiente.
Para mantener el código modular, la lógica específica de cada nodo del AST se
almacena en paquetes independientes. Los transpiladores a Python, JavaScript, ensamblador, Rust, C++, Go, R, Julia, Java, COBOL, Fortran, Pascal, Ruby, PHP, Matlab y LaTeX
importan estas funciones desde ``src.core.transpiler.python_nodes`` y
``src.core.transpiler.js_nodes`` (o ``asm_nodes`` o ``rust_nodes``) respectivamente, delegando la operación de
``visit_<nodo>`` a dichas funciones.

Para una visión esquemática de la interacción entre lexer, parser y transpiladores consulta :doc:`../../docs/arquitectura_parser_transpiladores`.

Módulos nativos
---------------
Bibliotecas básicas que amplían la funcionalidad de Cobra con
operaciones de E/S, utilidades matemáticas y estructuras de datos.

Helper de importaciones
-----------------------
El módulo ``src.cobra.transpilers.import_helper`` centraliza la gestión de
las importaciones. Ofrece una función para obtener las importaciones estándar
de cada lenguaje y otra que carga archivos según el ``module_map``
configurado. Los transpiladores utilizan este helper tanto al inicializar su
código como al resolver los ``import`` presentes en los programas.

Sistema de memoria
------------------
Gestiona de forma automática los recursos durante la ejecución para
optimizar el rendimiento y evitar fugas de memoria.

.. graphviz::
   :caption: Relación entre los módulos

   digraph cobra {
       rankdir=LR;
       subgraph cluster_core {
           label="Core";
           Lexer -> Parser -> AST;
           AST -> Interprete;
           AST -> Transpiladores;
       }
       CLI -> Lexer;
   Interprete -> Memoria;
   Interprete -> ModulosNativos;
   Transpiladores -> {Python JS Asm Rust Cpp Go R Julia Java COBOL Fortran Pascal Ruby PHP Matlab LaTeX};
   }
 
Interacción de los módulos
-------------------------
El flujo típico comienza con el ``Lexer`` que lee el código fuente y produce tokens. Estos tokens son consumidos por el ``Parser`` para construir el AST. A partir de este árbol el ``Intérprete`` ejecuta cada nodo o, alternativamente, los transpiladores lo recorren para generar código en otros lenguajes. Cuando se activa el modo seguro se aplica una cadena de validadores (ver :doc:`modo_seguro`) antes de ejecutar o generar código, bloqueando operaciones peligrosas.


Patrones de diseño
------------------
Cobra implementa diversos patrones para mantener su arquitectura flexible. El AST se recorre con el patrón *Visitor*, los transpiladores se obtienen desde la fábrica ``TRANSPILERS`` y los plugins de la CLI siguen el patrón *Command*. Consulta :doc:`design_patterns` para conocer los detalles.

Reporte de errores léxicos
--------------------------
El lexer genera tokens mientras mantiene un conteo de línea y columna.
Si encuentra un símbolo no reconocido detiene el proceso y lanza
``LexerError`` indicando la posición exacta del problema.

Diagrama de clases principal
----------------------------

.. graphviz:: uml/class_diagram.gv
   :caption: Estructura basica del nucleo

Diagrama de flujo general
------------------------

.. uml:: uml/arquitectura_general.puml
   :caption: Flujo del compilador y transpiladores

