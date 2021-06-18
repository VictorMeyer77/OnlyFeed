FROM oneoffcoder/rpi-scikit

COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN mkdir /models

RUN pip install --upgrade pip && pip install CurrencyConverter sklearn numpy psycopg2