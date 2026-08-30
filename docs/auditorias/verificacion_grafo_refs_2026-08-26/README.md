# Verificación del grafo y las referencias remotas

Fecha de ejecución: 2026-08-26 (UTC).

## Preparación del grafo

El clon no tenía un remoto configurado y era superficial. Se configuró `origin`
con `https://github.com/Alphonsus411/pCobra.git`, se obtuvieron todas las ramas y
etiquetas y, a continuación, se completó el historial con:

```text
$ git fetch --unshallow origin
$ git rev-parse --is-shallow-repository
false
```

La presencia del commit esperado y la conectividad de los objetos se comprobaron
sin errores:

```text
$ git cat-file -e 8b1676cdf52f30147ce42584a98ca4c421756369^{commit}
$ git fsck --full --no-dangling
```

## Referencias observadas

Después de completar el grafo se registraron las referencias remotas:

```text
$ git rev-parse origin/master
f684efc8a21d60eebcdce113cc8bfc21240ca37e
$ git rev-parse origin/fix/contrato-extensiones-cobra
b8ba487afd883f72de2a22fb5ecfed875e755357
```

## Relación entre ramas

El ancestro común coincide exactamente con el valor requerido:

```text
$ git merge-base origin/master origin/fix/contrato-extensiones-cobra
8b1676cdf52f30147ce42584a98ca4c421756369
```

El conteo inicial, con `master` a la izquierda y la rama de corrección a la
derecha, coincide con el valor de referencia:

```text
$ git rev-list --left-right --count origin/master...origin/fix/contrato-extensiones-cobra
1	327
```

Finalmente, ambas comprobaciones de ascendencia terminaron con código cero:

```text
$ git merge-base --is-ancestor 8b1676cdf52f30147ce42584a98ca4c421756369 origin/master
exit: 0
$ git merge-base --is-ancestor 8b1676cdf52f30147ce42584a98ca4c421756369 origin/fix/contrato-extensiones-cobra
exit: 0
```

## Conclusión

El grafo está completo, el merge-base existe y es el commit esperado. Ese commit
es ancestro de ambas referencias, por lo que no existe el bloqueo previsto para
historias inconexas y no se utilizó `--allow-unrelated-histories`.
