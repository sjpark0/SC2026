FROM python:3.12.9-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY npo-engine-lib /npo-engine-lib
COPY src/npo_cli_pipeline /app/src/npo_cli_pipeline
COPY pyproject.toml uv.lock README.md /app/
COPY . /app

RUN uv sync --project /app

CMD ["uv", "run", "npo-cli", "worker", "--loglevel", "INFO", "--pool", "solo", "--concurrency", "1"]
