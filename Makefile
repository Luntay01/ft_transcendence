PROJECT_DIR = ./project
DOCKER_COMPOSE = $(PROJECT_DIR)/docker-compose.yml
COMPOSE_CMD = docker compose -f $(DOCKER_COMPOSE)
ENV_FILE = $(PROJECT_DIR)/.env
BACKEND_CONTAINER = backend
NGINX_CONTAINER = nginx
FRONTEND_CONTAINER = frontend
WEBSOCKET_CONTAINER = websocket
AI_WORKER_CONTAINER = ai_worker
CLI_CONTAINER = cli_game
POSTGRES_CONTAINER = postgres
REDIS_CONTAINER = redis

all: up

docker-start:
	@echo "Starting Docker service (if required)..."
	@sudo systemctl start docker || echo "Docker is already running."

up: docker-start
	@echo "Building and starting containers in detached mode..."
	@$(COMPOSE_CMD) up -d --build

up-no-cache: docker-start
	@echo "Building and starting containers without cache..."
	@$(COMPOSE_CMD) build --no-cache
	@$(COMPOSE_CMD) up -d

start: docker-start
	@echo "Starting containers in detached mode (no build)..."
	@$(COMPOSE_CMD) up -d

down:
	@echo "Stopping and removing containers..."
	@$(COMPOSE_CMD) down

clean:
	@echo "Removing containers and volumes..."
	@$(COMPOSE_CMD) down -v

fclean:
	@echo "Removing containers, volumes, and images..."
	@$(COMPOSE_CMD) down -v --rmi all

re: clean up

prune:
	@echo "Cleaning up unused Docker resources..."
	@docker system prune -af --volumes

reset-db:
	@echo "Resetting the database..."
	@export $(shell cat $(PROJECT_DIR)/.env | xargs) && \
	$(COMPOSE_CMD) exec postgres psql -U $$POSTGRES_USER -d $$POSTGRES_DB -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

test:
	@echo "Running backend tests..."
	@$(COMPOSE_CMD) exec $(BACKEND_CONTAINER) python manage.py test

migrate:
	@echo "Running migrations..."
	@$(COMPOSE_CMD) exec $(BACKEND_CONTAINER) python manage.py makemigrations
	@$(COMPOSE_CMD) exec $(BACKEND_CONTAINER) python manage.py migrate

reload-nginx:
	@echo "Reloading NGINX configuration..."
	@$(COMPOSE_CMD) exec $(NGINX_CONTAINER) nginx -s reload

restart-%:
	@echo "Restarting $* container..."
	@if [ "$*" = "websocket" ]; then \
		$(COMPOSE_CMD) exec websocket pkill -f websocket_server.main || true; \
		sleep 2; \
	fi
	@$(COMPOSE_CMD) restart $*

shell-%:
	@echo "Accessing shell inside the $* container..."
	@docker exec -it $* /bin/sh

logs-%:
	@echo "Displaying logs for the $* container..."
	@docker logs $*

logs_stream-%:
	@echo "Displaying logs for the $* container..."
	@docker logs -f $*

logs:
	@echo "Displaying logs for all containers..."
	@$(COMPOSE_CMD) logs

help:
	@echo "Available commands:"
	@echo "  all					- Default target, starts containers."
	@echo "  start					- Starts containers in detached mode without rebuilding."
	@echo "  docker-start			- Starts Docker service if required."
	@echo "  up						- Builds and starts containers in detached mode."
	@echo "  up-no-cache			- Builds and starts containers without using the build cache."
	@echo "  down					- Stops and removes containers."
	@echo "  clean					- Removes containers and volumes."
	@echo "  fclean					- Removes containers, volumes, and images."
	@echo "  re						- Restarts the containers."
	@echo "  prune					- Prunes Docker system (removes unused resources)."
	@echo "  reset-db				- Resets the Postgres database."
	@echo "  test					- Runs backend tests."
	@echo "  migrate				- Runs Django migrations."
	@echo "  reload-nginx			- Reloads NGINX configuration."
	@echo "  restart-[name]			- Restarts the specified container."
	@echo "  shell-[name]			- Access shell in the specified container (e.g., backend, nginx)."
	@echo "  logs-[name]			- Display logs for the specified container."
	@echo "  logs_stream-[name]		- Display logs for the specified container continuesly."
	@echo "  logs					- Display logs for all containers."

.PHONY: all start up down clean fclean re prune reset-db test migrate reload-nginx logs help shell-% restart-%
