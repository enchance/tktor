#!/bin/bash

PG_CONTAINER=tktordb
REDIS_CONTAINER=tktorcache
SEEDERS_FILE=seeder.sql

# Account
echo "[Generating migrations...]"
alembic downgrade base \
    && rm -rf migrations/versions/* \
    && alembic revision --autogenerate \
    && alembic upgrade head \
    && echo '[Migrations complete]'

# Redis
echo "[Flushing redis...]"
docker exec -t $REDIS_CONTAINER bash -c "redis-cli FLUSHDB" \
    && echo "[Redis flushed]"

echo "[Seeding...]"
curl localhost:8000/dev/seed \
    && echo "[Seeding complete]"

# Postgres
echo "[Seeding sql...]"
docker exec -t $PG_CONTAINER psql -U vegeta -d vegeta -f /tmp/$SEEDERS_FILE \
    && echo "[SQL complete]"
