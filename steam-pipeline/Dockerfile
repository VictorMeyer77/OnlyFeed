FROM python:latest

COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN cd /app \
      && pip3 install --upgrade pip \
      && pip3 install -r requirements.txt