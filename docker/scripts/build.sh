#!/bin/sh

set -eu

# Imágenes Docker oficiales con runtime ejecutable en contenedor/sandbox
IMAGENES="cobra cobra-cpp cobra-js cobra-python cobra-rust"

# Build principal Cobra CLI

echo "[1/5] Construyendo cobra (docker/Dockerfile)"
docker build -t cobra -f docker/Dockerfile .

# Build por backend con runtime Docker oficial

echo "[2/5] Construyendo cobra-cpp (docker/backends/cpp.Dockerfile)"
docker build -t cobra-cpp -f docker/backends/cpp.Dockerfile .

echo "[3/5] Construyendo cobra-js (docker/backends/js.Dockerfile)"
docker build -t cobra-js -f docker/backends/js.Dockerfile .

echo "[4/5] Construyendo cobra-python (docker/backends/python.Dockerfile)"
docker build -t cobra-python -f docker/backends/python.Dockerfile .

echo "[5/5] Construyendo cobra-rust (docker/backends/rust.Dockerfile)"
docker build -t cobra-rust -f docker/backends/rust.Dockerfile .

echo "✅ Imágenes Docker construidas (ejecución en contenedor):"
for img in $IMAGENES; do
    docker image ls "$img"
done

echo "ℹ️ Política actual: los 8 targets oficiales de Cobra son python, rust, javascript, wasm, go, cpp, java y asm."
echo "ℹ️ Runtime Docker oficial solo para: python, javascript, cpp y rust."
echo "ℹ️ Targets solo transpilación (sin runtime Docker oficial): wasm, go, java y asm."
