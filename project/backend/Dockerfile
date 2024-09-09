# Django Backend
FROM python:3.9-slim
WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev

COPY ./backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./backend /app

COPY ./scripts/wait_for_depends_on.sh /wait_for_depends_on.sh
RUN chmod +x /wait_for_depends_on.sh

ENV DJANGO_SETTINGS_MODULE=backend.settings
ENV POSTGRES_DB=${POSTGRES_DB}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ENV REDIS_HOST=${REDIS_HOST}

CMD ["./wait_for_depends_on.sh", "postgres:5432", "--", "./wait_for_depends_on.sh", "redis:6379", "--", "python", "manage.py", "runserver", "0.0.0.0:8000"]