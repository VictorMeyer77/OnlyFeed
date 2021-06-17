FROM oneoffcoder/rpi-scikit:latest

COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN mkdir /models

RUN apt-get update

RUN cd /app \
      && pip install --upgrade pip \
      && pip install psycopg2 numpy CurrencyConverter