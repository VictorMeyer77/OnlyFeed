FROM python:latest

COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN mkdir /models

RUN apt-get update

RUN cd /app \
      && pip install --upgrade pip \
      && pip install sklearn psycopg2 numpy CurrencyConverter