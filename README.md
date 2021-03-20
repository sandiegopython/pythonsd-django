# San Diego Python Website

This is the repository for the San Diego Python website at [sandiegopython.org](https://sandiegopython.org).

[![Circle CI](https://circleci.com/gh/sandiegopython/pythonsd-django/tree/master.svg?style=shield)](https://circleci.com/gh/sandiegopython/pythonsd-django/tree/master)
[![AppVeyor](https://ci.appveyor.com/api/projects/status/6u1mssp3co57mi0g/branch/master?svg=true)](https://ci.appveyor.com/project/macro1/pythonsd-django/branch/master)
[![Requirements Status](https://requires.io/github/sandiegopython/pythonsd-django/requirements.svg?branch=master)](https://requires.io/github/sandiegopython/pythonsd-django/requirements/?branch=master)


## Developing

### Prerequisites

* Python 3.6+
* Node (12.x recommended)

### Getting started

```shell
pip install -r requirements/local.txt  # Install local Python requirements
npm Install                            # Install node dependencies for CSS/JS compiling
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
