# Librerías candidatas

Tras revisar `requirements.txt` y `requirements-dev.txt` se propone evaluar las siguientes librerías externas. Cada entrada incluye ventajas, posibles riesgos, un ejemplo de uso y el módulo donde podría integrarse.

## Pendulum
**Ventajas**
- Manejo intuitivo de fechas y zonas horarias.
- API compatible con `datetime` pero más expresiva.

**Riesgos**
- Aumenta el tamaño de las dependencias.
- Comunidad más pequeña que la librería estándar.

**Ejemplo**
```python
import pendulum
pendulum.parse("2024-01-01").add(days=1)
```
Se utilizaría para simplificar la manipulación de fechas en `src/standard_library/fecha.py`.

## NumPy
**Ventajas**
- Operaciones numéricas vectorizadas de alto rendimiento.
- Amplio ecosistema científico.

**Riesgos**
- Compilación pesada en algunos entornos.
- Puede ser excesivo para cálculos simples.

**Ejemplo**
```python
import numpy as np
np.mean([1, 2, 3])
```
Facilitaría operaciones complejas en `src/corelibs/numero.py`.

## Rich
**Ventajas**
- Salida en consola con colores y tablas.
- Mejor experiencia de depuración y logging.

**Riesgos**
- Incremento ligero de tiempos de inicio.
- Posible incompatibilidad con entornos mínimos.

**Ejemplo**
```python
from rich import print
print("[bold green]OK[/bold green]")
```
Podría mejorar mensajes de texto en `src/corelibs/texto.py`.

## HTTPX
**Ventajas**
- Cliente HTTP moderno con soporte síncrono y asíncrono.
- API similar a `requests`, facilitando la migración.

**Riesgos**
- Requiere comprender los conceptos de asincronía.
- Doble superficie de ataque al usar tanto sync como async.

**Ejemplo**
```python
import httpx
httpx.get("https://example.com")
```
Útil para enriquecer las capacidades de red en `src/corelibs/red.py`.

