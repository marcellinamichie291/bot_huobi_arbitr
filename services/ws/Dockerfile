# pull official base image
FROM python:3.9.5-slim-buster

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Europe/Moscow

# install system dependencies
RUN apt-get update && apt-get install -y netcat && apt-get install -y vim

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install ipdb
RUN pip install -r requirements.txt

# copy project
COPY . /app/

# run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
