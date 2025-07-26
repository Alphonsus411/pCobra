#!/bin/sh
set -e

echo "🛠️  Recibiendo código C++ desde stdin..."
cat > main.cpp

echo "🔧 Compilando con g++..."
g++ -std=c++17 -O2 -Wall -o main main.cpp

echo "🚀 Ejecutando programa compilado..."
./main

echo "🧹 Limpieza..."
rm -f main main.cpp

