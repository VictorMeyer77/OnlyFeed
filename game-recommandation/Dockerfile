FROM oneoffcoder/rpi-scikit

COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN mkdir /models

RUN pip3 install --upgrade pip && pip3 install CurrencyConverter sklearn numpy psycopg2