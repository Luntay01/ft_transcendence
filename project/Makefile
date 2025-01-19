
all: up

start: 
	@sudo systemctl start docker

up: start
	sudo docker compose up --build

down:
	sudo docker compose down

clean:
	sudo docker compose down -v

fclean:
	sudo docker compose down -v --rmi all

re: clean up

test:
	sudo docker exec -it project-backend-1 python manage.py test

migrate:
	sudo docker exec -it project-backend-1 python manage.py makemigrations

.PHONY: all up down clean fclean re test start migrate