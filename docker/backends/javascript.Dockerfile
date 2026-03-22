FROM node:20-slim

# Variables de entorno para evitar prompts interactivos
ENV NODE_ENV=production

# Directorio de trabajo
WORKDIR /work

# Copiar script opcional si lo deseas (sólo si lo usas)
# COPY script.js /work/script.js

# Este backend solo cubre runtime oficial de JavaScript; no implica soporte ejecutable para wasm/go/java/asm
# RUN npm install -g esbuild

# Entrypoint por defecto: evalúa JS desde stdin
ENTRYPOINT ["node", "-"]
