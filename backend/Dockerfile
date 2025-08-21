# backend/Dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local /usr/local
COPY . .
ENV PATH=/usr/local/bin:$PATH
EXPOSE 8000
# Use a shell command so the PORT environment variable is expanded at runtime
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips '*'" ]
