# Interfaces en Cobra

Cobra soporta la declaración de interfaces utilizando la palabra clave `interface`.
Las interfaces definen métodos abstractos que las clases pueden implementar.

```cobra
interface Printable:
    func mostrar()
fin

clase Documento(Printable):
    func mostrar():
        imprimir("doc")
    fin
fin
```

En los transpilers a Python, JavaScript, C++ y Rust se generan las construcciones equivalentes
(`class` abstracta, clase vacía, `struct` con métodos virtuales y `trait`).
