# Nginx Dockerfile
FROM nginx:latest

#COPY ./default.conf /etc/nginx/default.conf
#RUN apt-get update && apt-get install -y procps

RUN mkdir -p /home/app/staticfiles

COPY ./wait_for_depends_on.sh /wait_for_depends_on.sh
RUN chmod +x /wait_for_depends_on.sh

CMD ["./wait_for_depends_on.sh", "backend:8000", "--", "./wait_for_depends_on.sh", "frontend:3000", "--", "nginx", "-g", "daemon off;"]
