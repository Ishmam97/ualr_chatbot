FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* /app/

RUN pip install poetry && \
    poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi --only main --no-root

COPY backend /app/backend

ENV PYTHONPATH=/app

ENV LANGSMITH_TRACING=true
ENV LANGCHAIN_TRACING_V2=true
ENV LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
ENV LANGSMITH_API_KEY="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"
ENV LANGSMITH_PROJECT="ualr-chatbot"

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
