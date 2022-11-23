ARG PYTHON_VERSION=3.10-slim-buster

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    nodejs npm \
    make \
    build-essential \
    g++

RUN mkdir -p /code

WORKDIR /code

COPY . /code/

RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /code/requirements.txt && \
    pip install -r /code/requirements/local.txt && \
    rm -rf /root/.cache/

# Build static assets
RUN npm install
RUN npm run build

RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Increase the timeout since these PDFs take a long time to generate
CMD ["waitress-serve", "--port=8000", "config.wsgi:application"]
