
Avances del lenguaje Cobra
==========================

- **Lexer y Parser funcionales**: El sistema lexico y sintactico esta completamente implementado y es capaz de procesar asignaciones de variables, funciones, condicionales, bucles y operaciones de holobits.
- **Holobits**: Tipo de dato especial para trabajar con informacion multidimensional, con soporte para operaciones como proyecciones, transformaciones y visualizacion.
- **Gestión de memoria automatizada**: Cobra incluye un sistema de manejo de memoria optimizado que se ajusta automáticamente utilizando algoritmos genéticos.
- **Transpilacion a otros lenguajes**: Se ha implementado un transpilador que convierte el codigo Cobra a Python, JavaScript, ensamblador, Rust, C++, Go, Kotlin, Swift, R, Julia, Java, COBOL, Fortran, Pascal, Ruby, PHP, Perl, VisualBasic, Matlab, Mojo y LaTeX.
- **Pruebas unitarias**: Se han creado pruebas para validar el correcto funcionamiento del lexer y el parser.

 - **Versión 10.0.6**: Actualización de la documentación y configuración del proyecto.
 - **Versión 10.0.6**: Se incorpora ``pcobra.toml`` para definir el mapeo de módulos.

Versión 10.0.6
-----------
Se añade el archivo ``pcobra.toml`` para definir el mapeo de módulos en formato TOML. Su estructura es la siguiente:

.. code-block:: toml

   ["modulo.co"]
   python = "modulo.py"
   js = "modulo.js"

Compilación de extensiones C++ con PyBind11
------------------------------------------
El nuevo módulo ``pybind_bridge`` permite compilar código C++ usando
``pybind11`` y cargarlo como extensión de Python. El flujo habitual
consiste en llamar a ``compilar_y_cargar`` con el nombre del módulo y
el código fuente:

.. code-block:: python

   from cobra.core.nativos import compilar_y_cargar

   cpp = """
   #include <pybind11/pybind11.h>

   int duplicar(int x) { return x * 2; }

   PYBIND11_MODULE(mi_mod, m) {
       m.def("duplicar", &duplicar);
   }
   """

   mod = compilar_y_cargar("mi_mod", cpp)
   print(mod.duplicar(5))

Las funciones ``compilar_extension`` y ``cargar_extension`` están
disponibles si se requiere mayor control sobre el proceso.

Compilación de bibliotecas Rust
--------------------------------
El módulo ``rust_bridge`` permite compilar crates Rust utilizando
``cbindgen`` y ``cargo`` para generar bibliotecas compatibles con
``ctypes``. Basta con indicar la ruta del crate y el nombre de la
función a exponer:

.. code-block:: python

   from cobra.core.nativos import compilar_y_cargar_crate

   # Suponiendo un crate en ``./mi_crate`` con la función `triple`
   triple = compilar_y_cargar_crate("mi_crate", "triple")
   print(triple(3))

