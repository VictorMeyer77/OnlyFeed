FROM rasa/rasa-sdk:2.6.0

WORKDIR /app

USER root

COPY ./actions /app/actions
COPY ./conf /app/conf
COPY ./requirements.txt /app

RUN cd /app \
      && pip3 install --upgrade pip \
      && pip3 install -r requirements.txt

USER 1001