# Imagen base ligera con Python 3.9
FROM python:3.9-slim

# Variables de entorno recomendadas
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo
WORKDIR /app

# Copiar código fuente
COPY . /app

# Instalar dependencias del sistema (Rust para pybind11 y cbindgen)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        cargo \
        build-essential \
        git \
        curl \
        libssl-dev \
        && \
    cargo install cbindgen && \
    rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    pip install -e .

# Comando por defecto: ejecutar los tests
CMD ["pytest"]
