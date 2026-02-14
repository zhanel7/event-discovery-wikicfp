FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements/base.txt /app/requirements/
RUN pip install --no-cache-dir -r requirements/base.txt

COPY . /app/

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]