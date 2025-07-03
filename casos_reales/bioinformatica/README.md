# Ejemplo de Bioinformática

Este ejemplo calcula el porcentaje de GC de una secuencia almacenada en `secuencia.fasta`.

## Pasos para reproducir

1. Compila el código Cobra a Python:
   ```bash
   cobra compilar ejemplo_gc.cob --tipo python > ejemplo_gc.py
   ```
2. Ejecuta el script resultante:
   ```bash
   python ejemplo_gc.py > salida.txt
   ```
3. Verifica que `salida.txt` muestre el porcentaje de GC calculado.
