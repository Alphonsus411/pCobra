# Fixtures de regresión por feature

Cada feature nueva del lenguaje debe añadir un fixture mínimo en:

- `examples/features/<feature_id>/minimal.co`

El comando `cobra validar-sintaxis` descubre automáticamente estos fixtures y
los usa para regresión sintáctica de transpiladores oficiales.
