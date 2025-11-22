# San Diego Python Website

This is the repository for the San Diego Python website at [sandiegopython.org](https://sandiegopython.org).


## Developing

### Prerequisites

* [uv](https://docs.astral.sh) (see [uv installation](https://docs.astral.sh/uv/getting-started/installation/))
* Node v20


### Getting started

Install Python 3.14 with uv:

```shell
uv python install
```

Install dependencies and dev setup

```shell
uv sync --all-extras                    # Install local Python requirements
npm install                             # Install JS dependencies for frontend CSS/JS
npm run build                           # Build CSS (continuously with `npm run watch`)
uv run pre-commit install               # Setup code standard pre-commit hook
uv run ./manage.py migrate              # Create a local development database
uv run ./manage.py createsuperuser      # Create a local development administrator user
uv run ./manage.py runserver            # Starts a local development server at http://localhost:8000
```


## Testing

The entire test suite can be run with tox:

```shell
uv tool install tox --with tox-uv       # Install tox-uv (only needs to be run once ever)
tox
```

To test the Dockerfile that is used for deployment,
you can build the container and run it locally:

```shell
# Setup your local environment variables used with Docker
# This only needs to be run once
cp .env/local.sample .env/local

# Build the docker image for sandiegopython.org
# Use Docker compose to have Redis and PostgreSQL just like in production
# Note: Docker is used in production but Docker compose is just for development
make dockerbuild

# Start a development web server on http://localhost:8000
# Use ctrl+C to stop
make dockerserve

# While the server is running,
# you can start a bash shell to the container with the following:
# Once you have a bash shell, you can run migrations,
# manually connect to the local Postgres database or anything else
make dockershell
```


## Deploying

This site is deployed to [Fly.io](https://fly.io/).
It is deployed automatically when code is merged to the `main` branch
via GitHub Actions.


To deploy manually, you will need to be a member of the San Diego Python team on Fly.
Once you're a member of the team, you can deploy with:

```shell
make deploy
```
