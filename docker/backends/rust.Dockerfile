FROM rust:1.72-slim

# Variables de entorno recomendadas
ENV CARGO_HOME=/usr/local/cargo
ENV RUSTFLAGS="-C target-cpu=native"

# Directorio de trabajo
WORKDIR /work

# Instalar herramientas mínimas para compilación con rustc
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar script de compilación
COPY compile_rust.sh /usr/local/bin/compile_rust.sh
RUN chmod +x /usr/local/bin/compile_rust.sh

# Punto de entrada por defecto
ENTRYPOINT ["/usr/local/bin/compile_rust.sh"]
