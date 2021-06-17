FROM oneoffcoder/rpi-scikit:latest

COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN mkdir /models

RUN apt-get update
RUN apt-get install python3-pip -y
RUN apt-get install python3-psycopg2 gcc python3-dev musl-dev

RUN cd /app \
      && pip3 install --upgrade pip \
      && pip3 install -r requirements.txt