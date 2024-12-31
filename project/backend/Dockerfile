# Django Backend
FROM python:3.10-slim
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y libpq-dev

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY ./wait_for_depends_on.sh /wait_for_depends_on.sh
RUN chmod +x /wait_for_depends_on.sh


CMD ["sh", "-c", " \
    ./wait_for_depends_on.sh postgres:5432 -- \
    ./wait_for_depends_on.sh redis:6379 -- \
    python manage.py migrate && \
    python manage.py createsuperuser --id 1 --noinput || true && \
    python manage.py collectstatic --noinput && \
    python manage.py runserver 0.0.0.0:8000 \
"]

#CMD ["sh", "-c", "./wait_for_depends_on.sh postgres:5432 -- ./wait_for_depends_on.sh redis:6379 -- python manage.py migrate && python manage.py createsuperuser --noinput || true && python manage.py runserver 0.0.0.0:8000"]