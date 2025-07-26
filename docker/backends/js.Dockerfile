FROM node:20-slim

# Variables de entorno para evitar prompts interactivos
ENV NODE_ENV=production

# Directorio de trabajo
WORKDIR /work

# Copiar script opcional si lo deseas (sólo si lo usas)
# COPY script.js /work/script.js

# Puedes instalar herramientas JS si las usas desde Cobra o transpiler
# RUN npm install -g esbuild typescript

# Entrypoint por defecto: evalúa JS desde stdin
ENTRYPOINT ["node", "-"]
