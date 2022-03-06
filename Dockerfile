FROM python:3.7-slim

RUN mkdir /app
COPY app.py /app
COPY requirements.txt /app
COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["flask","run","--port","5105","--host=0.0.0.0"]
