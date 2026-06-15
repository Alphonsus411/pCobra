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

Una clase puede implementar varias interfaces a la vez o combinarlas con herencia de clases.

```cobra
interface Comprimible:
    func comprimir()
fin

clase Archivo(Printable, Comprimible):
    func mostrar():
        imprimir("archivo")
    fin
    func comprimir():
        imprimir("zip")
    fin
fin
```

En los transpilers oficiales públicos a `python`, `javascript` y `rust` se generan las construcciones equivalentes
(`class` abstracta, clase vacía y `trait`). Los ejemplos de `cpp` pertenecen a rutas históricas internas y no forman parte de la superficie pública.
