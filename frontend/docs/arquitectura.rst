Arquitectura de Cobra
=====================

El proyecto se divide en distintos componentes que interactúan para
ofrecer una experiencia completa de desarrollo:

CLI
---
La interfaz de línea de comandos permite ejecutar programas Cobra,
compilar a otros lenguajes y gestionar módulos instalados.

Core
----
Contiene el corazón del lenguaje: lexer, parser, intérprete y
transpiladores a Python y JavaScript. Estos elementos trabajan en
conjunto para analizar el código fuente y transformarlo en otras
representaciones o ejecutarlo de forma directa.

Módulos nativos
---------------
Bibliotecas básicas que amplían la funcionalidad de Cobra con
operaciones de E/S, utilidades matemáticas y estructuras de datos.

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
   Transpiladores -> {Python JS};
   }

Reporte de errores léxicos
--------------------------
El lexer genera tokens mientras mantiene un conteo de línea y columna.
Si encuentra un símbolo no reconocido detiene el proceso y lanza
``LexerError`` indicando la posición exacta del problema.
