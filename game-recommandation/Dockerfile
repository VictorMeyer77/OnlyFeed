FROM arm32v7/python

COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN mkdir /models

#RUN apt-get update

RUN pip install --upgrade pip && pip install CurrencyConverter sklearn numpy psycopg2