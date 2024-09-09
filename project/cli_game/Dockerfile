# CLI Pong Game
FROM python:3.9-slim
WORKDIR /app

COPY ./cli_game/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./cli_game /app

EXPOSE 8080

CMD ["python", "cli_pong.py"]