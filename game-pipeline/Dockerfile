FROM bde2020/spark-submit:3.1.1-hadoop3.2

COPY template.sh /
COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN cd /app \
      && pip3 install -r requirements.txt