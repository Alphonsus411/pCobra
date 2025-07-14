# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends cargo && \
    cargo install cbindgen && \
    pip install -r requirements.txt && \
    pip install -e .

CMD ["pytest"]
