FROM python:3.11.4-alpine

WORKDIR /usr/src/app

# prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# ensure Python output is sent directly to the terminal without buffering
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./faucetapi/requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY ./faucetapi /usr/src/app/
COPY .env /usr/src/app/.env

# ENTRYPOINT ["/bin/ash"]
ENTRYPOINT ["/usr/src/app/docker_entrypoint.sh"]