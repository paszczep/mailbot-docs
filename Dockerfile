FROM ghcr.io/astral-sh/uv:python3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

RUN apk add subversion

COPY requirements.txt ./

RUN uv pip install \
    --requirement requirements.txt \
    --system

COPY app/ app/

COPY emails.toml ./

CMD ["python", "-m", "app"]
