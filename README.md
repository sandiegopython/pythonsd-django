# San Diego Python Website

This is the repository for the San Diego Python website at [sandiegopython.org](https://sandiegopython.org).

[![AppVeyor](https://ci.appveyor.com/api/projects/status/184l9lc8y7av2fah?svg=true)](https://ci.appveyor.com/project/davidfischer/pythonsd-django)
[![Requirements Status](https://requires.io/github/sandiegopython/pythonsd-django/requirements.svg?branch=main)](https://requires.io/github/sandiegopython/pythonsd-django/requirements/?branch=main)


## Developing

### Prerequisites

* Python 3.7+
* Node (12.x recommended)

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
