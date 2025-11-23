# https://www.debian.org/releases/stable/
# https://hub.docker.com/_/python/
ARG PYTHON_VERSION=3.14-slim-trixie

FROM python:${PYTHON_VERSION}

LABEL maintainer="https://github.com/sandiegopython"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# uv environment variables
# Copy (don't hardlink) files into /.venv. Avoid issues with Docker's FS
# https://docs.astral.sh/uv/reference/environment/
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=never
ENV UV_PROJECT_ENVIRONMENT=/.venv

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
    postgresql-client libpq-dev \
    git

RUN mkdir -p /code /home/www/
WORKDIR /code

# Install uv for fast package management
# https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.9.11 /uv /uvx /bin/

# Copy project files for dependency resolution
# uv.lock ensures reproducible builds
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --all-extras

COPY . /code/

# Build JS/static assets
RUN --mount=type=cache,target=/root/.npm npm install
RUN npm run dist

RUN uv run python manage.py collectstatic --noinput --clear

# Launches the application (gunicorn) with this script
COPY ./docker/start /start
RUN chmod +x /start

# Launch a shell within the container with this script
COPY ./docker/shell /shell
RUN chmod +x /shell

# Run the container unprivileged
RUN addgroup www && useradd -g www www
RUN chown -R www:www /code
# Needed for the uv cache
RUN chown -R www:www /home/www
USER www

# Output information about the build
# These files can be read by the application
RUN git log -n 1 --pretty=format:"%h" > GIT_COMMIT
RUN date -u +'%Y-%m-%dT%H:%M:%SZ' > BUILD_DATE

EXPOSE 8000

CMD ["/start"]
