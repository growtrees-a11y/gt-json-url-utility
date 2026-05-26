# ---- Build stage ----
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

COPY . .
RUN python -m pytest -v --tb=short || true

# ---- Runtime stage ----
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --from=builder /app /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
