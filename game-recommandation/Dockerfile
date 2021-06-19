FROM python:latest

COPY app/. /app
COPY conf/. /conf

RUN mkdir /models

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install libblas3 liblapack3 liblapack-dev libblas-dev gfortran

RUN pip install --upgrade pip
RUN pip install numpy scipy joblib threadpoolctl
RUN pip install CurrencyConverter sklearn psycopg2