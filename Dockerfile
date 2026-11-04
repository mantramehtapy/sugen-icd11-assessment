FROM python:3.11-slim

WORKDIR /app
COPY app /app/app
COPY public/data /app/public/data

ENTRYPOINT ["python", "-m", "app"]
