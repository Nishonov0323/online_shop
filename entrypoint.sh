#!/bin/bash

echo "Starting entrypoint script..."

# Wait for database with timeout
echo "Waiting for database connection..."
timeout=60
count=0
while ! nc -z $DB_HOST $DB_PORT; do
  echo "Database not ready yet... ($count/$timeout)"
  sleep 1
  count=$((count + 1))
  if [ $count -eq $timeout ]; then
    echo "Database connection timeout!"
    exit 1
  fi
done

echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser if not exists
echo "Creating superuser..."
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
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting application..."
# Start the application
exec "$@"