# pull official base image
FROM python:3.9.5-slim-buster

# set work directory
WORKDIR /usr/src/webapp

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Europe/Moscow

# install system dependencies
RUN apt-get update && apt-get install -y netcat && apt-get install -y vim

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/webapp/requirements.txt
RUN pip install ipdb
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/webapp/

# run entrypoint.sh
ENTRYPOINT ["/usr/src/webapp/entrypoint.sh"]