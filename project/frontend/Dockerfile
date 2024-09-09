# Frontend (vanilla JS/Bootstrap app)
FROM node:16-alpine
WORKDIR /app

COPY ./frontend/package.json ./frontend/package-lock.json /app/
RUN npm install

COPY ./frontend /app

COPY ./scripts/wait_for_depends_on.sh /wait_for_depends_on.sh
RUN chmod +x /wait_for_depends_on.sh

CMD ["./wait_for_depends_on.sh", "backend:8000", "--", "npm", "start"]