#!/bin/ash

echo "Load environment variables"
set -a && source .env && set +a

echo "Create django superuser without interactive input"
python manage.py createsuperuser --noinput

# python ./faucetapi/manage.py runserver 59080

echo "Apply database migrations"
python manage.py migrate

exec "$@"