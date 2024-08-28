set -a && source .env && set +a
./faucetapi/manage.py createsuperuser --noinput
./faucetapi/manage.py test faucet.tests