ARG PYTHON_VERSION=3.10-slim-buster

FROM python:${PYTHON_VERSION}

LABEL maintainer="https://github.com/sandiegopython"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    nodejs npm \
    make \
    build-essential \
    g++ \
    git

RUN mkdir -p /code

WORKDIR /code

COPY . /code/

RUN set -ex && \
    pip install --upgrade --no-cache-dir pip && \
    pip install --no-cache-dir -r /code/requirements.txt && \
    pip install --no-cache-dir -r /code/requirements/local.txt

# Build static assets
RUN npm install
RUN npm run build

RUN python manage.py collectstatic --noinput

# Run the container unprivileged
RUN addgroup www && useradd -g www www
RUN chown -R www:www /code
USER www

# Output information about the build
# These files can be read by the application
RUN git log -n 1 --pretty=format:"%h" > GIT_COMMIT
RUN date -u +'%Y-%m-%dT%H:%M:%SZ' > BUILD_DATE

EXPOSE 8000

# Increase the timeout since these PDFs take a long time to generate
CMD ["waitress-serve", "--port=8000", "config.wsgi:application"]
