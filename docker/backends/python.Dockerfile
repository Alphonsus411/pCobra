FROM python:3.11-slim

# Evitar bytecode y buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo
WORKDIR /work

# Instalar pip y setuptools actualizados (opcional)
RUN pip install --upgrade pip setuptools wheel

# Entrypoint por defecto: evalúa código Python desde stdin
ENTRYPOINT ["python", "-u", "-"]
