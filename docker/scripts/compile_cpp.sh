#!/bin/sh
cat > main.cpp
g++ -std=c++17 main.cpp -o main && ./main
