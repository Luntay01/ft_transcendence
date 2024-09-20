# Custom PostgreSQL
FROM postgres:13

RUN apt-get update && apt-get install -yq gettext-base

COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

COPY ./init.sql /docker-entrypoint-initdb.d/init.sql

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["postgres"]