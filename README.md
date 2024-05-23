# San Diego Python Website

This is the repository for the San Diego Python website at [sandiegopython.org](https://sandiegopython.org).

[![AppVeyor](https://ci.appveyor.com/api/projects/status/184l9lc8y7av2fah?svg=true)](https://ci.appveyor.com/project/davidfischer/pythonsd-django)


## Developing

### Prerequisites

* Python v3.10
* Node v20

### Getting started

```shell
pip install -r requirements/local.txt  # Install local Python requirements
npm install                            # Install node dependencies for CSS/JS compiling
npm run build                          # Build CSS/JS
pre-commit install                     # Setup code standard pre-commit hook
./manage.py migrate                    # Create a local development database
./manage.py createsuperuser            # Create a local development administrator user
./manage.py runserver                  # Starts a local development server at http://localhost:8000
```


## Testing

The entire test suite can be run with tox:

```shell
tox
```

To test the Dockerfile that is used for deployment,
you can build the container and run it locally:

```shell
# Setup your local environment variables used with Docker
# This only needs to be run once
cp .env/local.sample .env/local

# Build the docker image for sandiegopython.org
docker buildx build -t sandiegopython.org .

# Start a development server on http://localhost:8000
docker run --env-file=".env/local" --publish=8000:8000 sandiegopython.org

# You can start a shell to the container with the following:
docker run --env-file=".env/local" -it sandiegopython.org /bin/bash
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
