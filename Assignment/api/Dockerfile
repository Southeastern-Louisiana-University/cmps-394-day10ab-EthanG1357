FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get upgrade -y && apt-get clean

RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy psycopg2-binary requests

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]