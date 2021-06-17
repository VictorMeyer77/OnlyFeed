FROM python:latest

COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN mkdir /models

#RUN sudo apt-get install gfortran libopenblas-dev liblapack-dev
RUN apt-get update

RUN cd /app \
      && pip3 install --upgrade pip \
      && pip3 psycopg2 numpy CurrencyConverter sklearn

