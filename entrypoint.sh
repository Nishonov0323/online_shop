#!/bin/bash

# Wait for postgres
if [ "$DATABASE" = "postgres" ] || [ -z "$DATABASE" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Apply database migrations
echo "Applying migrations..."
python manage.py migrate

# Create superuser if doesn't exist
echo "Creating superuser..."
python manage.py createsuperuser --noinput || true

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"