FROM show0k/miniconda-armv7

COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN mkdir /models

#RUN apt-get update

RUN export PATH="/opt/conda/bin:${PATH}" && conda install sklearn numpy psycopg2
RUN pip install --upgrade pip && pip install CurrencyConverter