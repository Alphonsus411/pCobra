# Instalación avanzada

Esta guía cubre escenarios más complejos que la instalación básica descrita en el README.

## Instalación desde repositorio

```bash
git clone https://github.com/Alphonsus411/pCobra.git
cd pCobra
./scripts/install_dev.sh      # dependencias de desarrollo
# o
./scripts/install.sh --dev            # instala en modo editable
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

Copia `.env.example` a `.env` y verifica la instalación con `cobra --version`.

## Recrear el entorno con herramientas estándar

Si prefieres evitar los scripts incluidos en el repositorio, estos pasos usan
únicamente `python`, `venv` y `pip` para levantar un entorno desde cero:

1. Crea un entorno virtual aislado:
   ```bash
   python -m venv .venv
   ```
2. Activa el entorno:
   ```bash
   source .venv/bin/activate      # Linux o macOS
   .\\.venv\\Scripts\\activate  # Windows
   ```
3. Actualiza `pip` y `setuptools` para evitar incompatibilidades:
   ```bash
   python -m pip install --upgrade pip setuptools
   ```
4. Instala pCobra en modo editable junto con las dependencias básicas:
   ```bash
   pip install -e .
   ```
5. Añade las dependencias de desarrollo y pruebas cuando las necesites:
   ```bash
   pip install -r requirements-dev.txt
   ```

Con este flujo puedes recrear rápidamente un entorno limpio después de limpiar
el árbol de trabajo o al migrar a una máquina nueva.

## Instalación de gramáticas

Algunos transpiladores inversos utilizan [tree-sitter](https://tree-sitter.github.io/tree-sitter/).
Instala las gramáticas con:

```bash
pip install tree-sitter-languages
```

## Instalación de plugins

Los plugins son paquetes de Python registrados bajo `cobra.plugins`.
Para usar uno publicado:

```bash
pip install mi-plugin-cobra
```

Para un plugin local en modo editable:

```bash
pip install -e ./mi_plugin
cobra plugins           # lista plugins disponibles
```

## Docker

### Construir la imagen localmente

```bash
docker build -t cobra-cli -f docker/Dockerfile .
# o
cobra contenedor --tag cobra-cli
```

### Ejecutar comandos

```bash
docker run --rm cobra-cli --version
docker run --rm -v "$(pwd)":/src cobra-cli ejecutar /src/ejemplos/hola.cobra
```

### Imagen publicada por CI

Obtén la última versión con:

```bash
docker pull alphonsus411/cobra:latest
```
