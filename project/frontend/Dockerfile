# Frontend (vanilla JS/Bootstrap app)
FROM node:16-alpine
WORKDIR /app

RUN apk add --no-cache bash

COPY ./package.json ./package-lock.json /app/
RUN npm install

COPY . /app

COPY ./wait_for_depends_on.sh /wait_for_depends_on.sh
RUN chmod +x /wait_for_depends_on.sh

CMD ["bash", "-c", "./wait_for_depends_on.sh backend:8000 -- npm start"]