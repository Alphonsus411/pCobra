# Instalación avanzada

Esta guía cubre escenarios más complejos que la instalación básica descrita en el README.

## Instalación desde repositorio

```bash
git clone https://github.com/Alphonsus411/pCobra.git
cd pCobra
./scripts/install_dev.sh      # dependencias de desarrollo
# o
./install.sh --dev            # instala en modo editable
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

Copia `.env.example` a `.env` y verifica la instalación con `cobra --version`.

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
