# Stage de construcción: prepara entorno y compila el CLI
FROM python:3.11-slim AS builder

# Variables de entorno recomendadas
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro de la imagen
WORKDIR /app

# Instalar dependencias de compilación necesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        cargo \
        git \
        curl \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar el código fuente
COPY . /app

# Instalar el proyecto y PyInstaller
RUN pip install --upgrade pip setuptools wheel && \
    pip install . && \
    pip install pyinstaller

# Compilar el binario del CLI
RUN pyinstaller cobra-cli.spec

# Stage final minimalista que sólo incluye el binario
FROM gcr.io/distroless/base-debian12

# Copiar el artefacto generado desde el builder
COPY --from=builder /app/dist/cobra-cli /usr/local/bin/cobra-cli

# Punto de entrada que ejecuta el binario del CLI
ENTRYPOINT ["/usr/local/bin/cobra-cli"]
