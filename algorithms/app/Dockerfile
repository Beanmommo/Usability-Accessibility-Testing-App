FROM alpine:3.14 as base

ENV PYTHONUNBUFFERED=1

RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN apk add py3-pip bash curl python3-dev gcc zlib-dev libffi-dev postgresql-dev musl-dev jpeg-dev

RUN python3 -m ensurepip

RUN pip3 install --no-cache --upgrade pip setuptools

# RUN pip install pip==22.2.2

RUN pip install --upgrade pip \
  && rm -rf /var/cache/apk/*

# SET environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# webservice dependencies
#Server will reload itself on file changes if in dev mode
ENV FLASK_ENV=development 
RUN pip3 install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

# expose 3050
EXPOSE 3050

WORKDIR /opt/app
COPY . .