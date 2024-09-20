# AI Worker
FROM python:3.10-slim

WORKDIR /app

#no need postgres here we will iteract wiwth redis
#RUN apt-get update && apt-get install -y libpq-dev
RUN apt-get update && apt-get install -yq --no-install-recommends curl

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
COPY ./wait_for_depends_on.sh /wait_for_depends_on.sh
RUN chmod +x /wait_for_depends_on.sh

CMD ["./wait_for_depends_on.sh", "redis:6379", "--", "celery", "-A", "ai_worker", "worker"]