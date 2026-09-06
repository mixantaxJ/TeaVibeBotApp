FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create a non-root user and group
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -m appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create the qdrant data directory and set permissions
RUN mkdir -p /app/data/qdrant && \
    chown -R appuser:appgroup /app/data

USER appuser

CMD ["python", "-m", "rag_bot.bot"]
