# CLI Pong Game
FROM python:3.10-slim
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -q

COPY . /app

COPY ./wait_for_depends_on.sh /wait_for_depends_on.sh
RUN chmod +x /wait_for_depends_on.sh

CMD ["./wait_for_depends_on.sh", "websocket:8765", "--", "python", "cli_pong.py"]