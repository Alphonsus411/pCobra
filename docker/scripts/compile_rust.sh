#!/bin/sh
cat > main.rs
rustc main.rs -O -o main && ./main
