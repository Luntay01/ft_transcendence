# WebSocket server
FROM python:3.10-slim
WORKDIR /app

#no libpq-dev since not needed
#RUN apt-get update && apt-get install -y libpq-dev
RUN apt-get update && apt-get install -yq --no-install-recommends curl procps

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -q

COPY . /app

COPY ./wait_for_depends_on.sh /wait_for_depends_on.sh
RUN chmod +x /wait_for_depends_on.sh

CMD ["./wait_for_depends_on.sh", "backend:8000", "--", "python", "-m", "websocket_server.main"]
#CMD ["sh", "-c", "./wait_for_depends_on.sh backend:8000 -- python -m websocket_server.main & tail -f /dev/null"]
