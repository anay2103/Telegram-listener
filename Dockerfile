FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1
ENV PATH "/app/:${PATH}"

EXPOSE 80
WORKDIR /app

RUN set -ex &&  apt update && apt upgrade -y && rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock /app/
COPY ./docker-entrypoint.sh /docker-entrypoint.sh

RUN pip install pipenv
RUN pipenv install --deploy --system

COPY . /app/
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]