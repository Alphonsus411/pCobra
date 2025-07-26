FROM gcc:12-slim

# Variables opcionales
ENV DEBIAN_FRONTEND=noninteractive

# Directorio de trabajo
WORKDIR /work

# Instalar herramientas útiles
RUN apt-get update && apt-get install -y --no-install-recommends \
    make cmake gdb \
    && rm -rf /var/lib/apt/lists/*

# Copiar el script de compilación
COPY compile_cpp.sh /usr/local/bin/compile_cpp.sh
RUN chmod +x /usr/local/bin/compile_cpp.sh

# Exponer el punto de entrada del compilador
ENTRYPOINT ["/usr/local/bin/compile_cpp.sh"]
