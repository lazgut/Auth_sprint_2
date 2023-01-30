FROM python:3.10-alpine AS app_auth

WORKDIR /app
ARG DOCKER_USER_ID
ARG DOCKER_GROUP_ID
RUN addgroup -g $DOCKER_GROUP_ID app && \
    adduser --disabled-password --no-create-home --uid $DOCKER_USER_ID --ingroup app app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /app
RUN apk add -U --no-cache build-base && \
 pip install -r /app/requirements.txt && \
 pip install gunicorn && \
 apk del build-base

COPY ./src /app
USER app
CMD ["gunicorn", "--worker-class", "gevent", "wsgi:create_app()"]

# Nginx image
FROM nginx:1-alpine AS app_nginx
WORKDIR /srv/app
COPY docker/nginx/default.conf /etc/nginx/conf.d
