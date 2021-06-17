FROM debian:latest

COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN mkdir /models

RUN apt-get update
RUN apt-get install build-essential python3-dev python3-pip -y
RUN apt-get install cython3 python3-psycopg2 python3-numpy python3-scipy -y

RUN cd /app \
      && pip3 install --upgrade pip \
      && pip3 install sklearn CurrencyConverter