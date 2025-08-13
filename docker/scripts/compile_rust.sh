#!/bin/sh
set -e

echo "🦀 Recibiendo código Rust desde stdin..."
cat > main.rs

echo "🔧 Compilando con rustc..."
# -C opt-level=3   : maximiza las optimizaciones
# -C lto           : habilita Link Time Optimization
# -C strip=symbols : remueve símbolos para reducir el tamaño final
rustc -C opt-level=3 -C lto -C strip=symbols main.rs -o main

echo "🚀 Ejecutando..."
./main

echo "🧹 Limpiando archivos temporales..."
rm -f main main.rs
