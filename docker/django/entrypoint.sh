#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
until python -c "
import psycopg, os
psycopg.connect(
    host=os.environ.get('DB_HOST', 'localhost'),
    port=os.environ.get('DB_PORT', 5432),
    dbname=os.environ.get('DB_NAME', 'cassa'),
    user=os.environ.get('DB_USER', 'cassa'),
    password=os.environ.get('DB_PASSWORD', 'cassa'),
).close()
" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL ready."

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

exec "$@"
