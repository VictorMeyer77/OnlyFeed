FROM python:latest

COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN mkdir /models

#RUN apt-get -y update
#RUN apt-get -y upgrade
#RUN apt-get -y install python3-pip postgresql-server-dev-all gcc python3-dev musl-dev libpq-dev

#RUN pip3 install --upgrade pip && pip3 install CurrencyConverter sklearn numpy psycopg2-binary