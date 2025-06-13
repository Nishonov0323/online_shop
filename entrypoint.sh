#!/bin/bash

# Wait for database
while ! nc -z $DB_HOST $DB_PORT; do
  echo "Waiting for database..."
  sleep 1
done

echo "Database is ready!"

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser if not exists
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Collect static files
python manage.py collectstatic --noinput

# Start the application
exec "$@"