FROM python:3.11.9-alpine3.19

COPY ./api /api
COPY ./util /util
COPY requirements.txt .
COPY app.py .

RUN pip install -r requirements.txt
