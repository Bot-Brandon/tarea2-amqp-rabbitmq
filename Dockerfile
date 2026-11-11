FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends tcpdump \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY laboratorio.py capturar.sh ./
ENTRYPOINT ["sh", "/app/capturar.sh"]
