FROM python:latest

COPY app/. /app
COPY requirements.txt /app/
COPY conf/. /conf

RUN cd /app \
      && pip3 install --upgrade pip \
      && pip3 install -r requirements.txt

RUN python -m nltk.downloader words
RUN python -m nltk.downloader stopwords
RUN python -m nltk.downloader punkt
RUN python -m nltk.downloader vader_lexicon
RUN python -m spacy download en_core_web_lg