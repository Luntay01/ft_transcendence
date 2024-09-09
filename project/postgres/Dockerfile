# Custom PostgreSQL
FROM postgres:13

# add custom configurations if needed
COPY ./postgres/postgresql.conf /etc/postgresql/postgresql.conf
COPY ./postgres/init.sql /docker-entrypoint-initdb.d/init.sql

EXPOSE 5432