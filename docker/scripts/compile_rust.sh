#!/bin/sh
set -e

echo "🦀 Recibiendo código Rust desde stdin..."
cat > main.rs

echo "🔧 Compilando con rustc..."
rustc main.rs -O -o main

echo "🚀 Ejecutando..."
./main

echo "🧹 Limpiando archivos temporales..."
rm -f main main.rs
