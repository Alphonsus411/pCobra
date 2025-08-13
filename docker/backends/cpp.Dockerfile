FROM gcc:12-slim

# Variables opcionales
ENV DEBIAN_FRONTEND=noninteractive

# Directorio de trabajo
WORKDIR /work

# Copiar el script de compilación
COPY compile_cpp.sh /usr/local/bin/compile_cpp.sh
RUN chmod +x /usr/local/bin/compile_cpp.sh

# Exponer el punto de entrada del compilador
ENTRYPOINT ["/usr/local/bin/compile_cpp.sh"]
