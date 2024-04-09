FROM python:3.11

COPY ./api /api
COPY ./util /util
COPY requirements.txt .
COPY app.py .

RUN pip install -r reqirements.txt
