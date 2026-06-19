#!/bin/sh

set -eu

# Imágenes Docker oficiales con runtime ejecutable en contenedor/sandbox
IMAGENES="cobra cobra-python cobra-javascript cobra-rust"

# Build principal Cobra CLI

echo "[1/4] Construyendo cobra (docker/Dockerfile)"
docker build -t cobra -f docker/Dockerfile .

# Build por backend con runtime Docker oficial

echo "[2/4] Construyendo cobra-javascript (docker/backends/javascript.Dockerfile)"
docker build -t cobra-javascript -f docker/backends/javascript.Dockerfile .

echo "[3/4] Construyendo cobra-python (docker/backends/python.Dockerfile)"
docker build -t cobra-python -f docker/backends/python.Dockerfile .

echo "[4/4] Construyendo cobra-rust (docker/backends/rust.Dockerfile)"
docker build -t cobra-rust -f docker/backends/rust.Dockerfile .

echo "✅ Imágenes Docker construidas (ejecución en contenedor):"
for img in $IMAGENES; do
    docker image ls "$img"
done

echo "ℹ️ Política actual: los 3 targets oficiales de Cobra son python, javascript y rust."
echo "ℹ️ Runtime Docker oficial solo para: python, javascript y rust."
echo "ℹ️ Targets legacy retirados no se construyen como BackEnd público."
