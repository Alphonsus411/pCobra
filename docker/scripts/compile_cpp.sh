#!/bin/sh
set -e

echo "🛠️  Recibiendo código C++ desde stdin..."
cat > main.cpp

echo "🔧 Compilando con g++..."
# -O3  : maximiza las optimizaciones
# -flto: realiza optimización en tiempo de enlace
# -s   : elimina símbolos para reducir el tamaño del binario
g++ -std=c++17 -O3 -flto -s -Wall -o main main.cpp

echo "🚀 Ejecutando programa compilado..."
./main

echo "🧹 Limpieza..."
rm -f main main.cpp

