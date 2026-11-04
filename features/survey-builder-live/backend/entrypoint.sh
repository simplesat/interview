#!/bin/sh
set -e

until nc -z "${POSTGRES_HOST:-db}" "${POSTGRES_PORT:-5432}"; do
  echo "Waiting for the database..."
  sleep 1
done

python manage.py migrate --noinput
python manage.py seed
exec python manage.py runserver 0.0.0.0:8000
