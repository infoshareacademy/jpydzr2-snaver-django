# syntax=docker/dockerfile:1
FROM python:3.9-buster
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
EXPOSE 80
ENV PYTHONUNBUFFERED=1
STOPSIGNAL SIGTERM
CMD python manage.py runserver 0.0.0.0:80