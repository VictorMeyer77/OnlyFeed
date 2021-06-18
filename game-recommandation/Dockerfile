FROM oneoffcoder/rpi-scikit

COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN mkdir /models

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install python3-pip

RUN pip3 install --upgrade pip && pip3 install CurrencyConverter sklearn numpy psycopg2-binary