FROM python:3.12.3-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements1.txt .
RUN pip install --no-cache-dir -r requirements1.txt

RUN pip install gunicorn

COPY ./myproject/ ./myproject/
COPY ./.env .

ENV PYTHONUNBUFFERED=1

WORKDIR /app/myproject

RUN python3 manage.py collectstatic --noinput

EXPOSE 80

CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 myproject.wsgi:application"]
