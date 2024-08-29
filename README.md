
## Getting started
Just run `docker-compose up -d --build` in the root directory

This should spawn the following containers: 
* django - RESTful API
* celery - asynchronous task for ETH transaction confirmation
* rabbitmq - celery message broker
* redis - celery result backend
* prometheus - monitoring of django container
* grafana

## Note 
There is no `.env` file pushed in this repository. It should contain the following env variables:
```
DEBUG=
DJANGO_SUPERUSER_USERNAME=
DJANGO_SUPERUSER_EMAIL=
DJANGO_SUPERUSER_PASSWORD=
CELERY_BROKER="amqp://guest:guest@rabbitmq:5672/"
CELERY_BACKEND="redis://redis:6379/0"
DEPOSIT_WALLET_PRIVATE_KEY=
ETHEREUM_NODE_URL=
NETWORK_ID=
```
