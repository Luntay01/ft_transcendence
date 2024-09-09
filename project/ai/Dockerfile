# AI Worker
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev

COPY ./ai/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ai /app

COPY ./scripts/wait_for_depends_on.sh /wait_for_depends_on.sh
RUN chmod +x /wait_for_depends_on.sh

CMD ["./wait_for_depends_on.sh", "redis:6379", "--", "celery", "-A", "ai_worker", "worker"]