#!/bin/sh

# Build principal Cobra
docker build -t cobra -f docker/Dockerfile .

# Build por lenguaje (transpilers)
docker build -t cobra-cpp -f docker/cpp.Dockerfile .
docker build -t cobra-js -f docker/js.Dockerfile .
docker build -t cobra-python -f docker/python.Dockerfile .
docker build -t cobra-rust -f docker/rust.Dockerfile .

echo "✅ Imágenes construidas:"
docker images | grep cobra

