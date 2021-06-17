FROM oneoffcoder/rpi-scikit:latest

COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN mkdir /models

RUN apt-get update && apt-get install python3-pip

RUN cd /app \
      && pip3 install --upgrade pip \
      && pip3 install psycopg2 numpy CurrencyConverter