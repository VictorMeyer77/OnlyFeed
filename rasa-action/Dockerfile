FROM rasa/rasa-sdk:2.6.0

WORKDIR /app

USER root

COPY ./actions /app/actions

RUN pip install --requirement /app/actions/requirements-actions.txt

USER 1001