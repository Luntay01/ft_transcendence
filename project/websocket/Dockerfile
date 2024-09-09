# WebSocket server
FROM python:3.9-slim
WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev

COPY ./websocket/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./websocket /app

COPY ./scripts/wait_for_depends_on.sh /wait_for_depends_on.sh
RUN chmod +x /wait_for_depends_on.sh

CMD ["./wait_for_depends_on.sh", "backend:8000", "--", "python", "ws_server.py"]