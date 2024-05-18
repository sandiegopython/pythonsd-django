ARG PYTHON_VERSION=3.10-slim-buster

FROM python:${PYTHON_VERSION}

LABEL maintainer="https://github.com/sandiegopython"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y --no-install-recommends curl

# Install Node v20
# This should be run before apt-get install nodejs
# https://github.com/nodesource/distributions
RUN curl -sL https://deb.nodesource.com/setup_20.x | bash -

RUN apt-get install -y --no-install-recommends \
    nodejs \
    make \
    build-essential \
    g++ \
    git

RUN mkdir -p /code

WORKDIR /code

COPY . /code/

# Cache dependencies when building which should result in faster docker builds
RUN --mount=type=cache,target=/root/.cache/pip set -ex && \
    pip install --upgrade --no-cache-dir pip && \
    pip install -r /code/requirements.txt && \
    pip install -r /code/requirements/local.txt

# Build JS/static assets
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

CMD ["gunicorn", "--timeout", "15", "--bind", ":8000", "--workers", "2", "--max-requests", "10000", "--max-requests-jitter", "100", "config.wsgi"]
