FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod +x /install.sh && /install.sh && rm /install.sh
ENV PATH="/root/.local/bin:${PATH}" 
WORKDIR /app

COPY requirements.txt .

RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install -r requirements.txt

FROM python:3.13-slim-bookworm AS production

WORKDIR /app
COPY . .
COPY --from=builder /app/.venv .venv

ENV PATH="/app/.venv/bin:$PATH"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
