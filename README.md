# SDPUG Django Site

[![Circle CI](https://circleci.com/gh/pythonsd/pythonsd-django/tree/master.svg?style=shield)](https://circleci.com/gh/pythonsd/pythonsd-django/tree/master)
[![AppVeyor](https://ci.appveyor.com/api/projects/status/6u1mssp3co57mi0g/branch/master?svg=true)](https://ci.appveyor.com/project/macro1/pythonsd-django/branch/master)
[![Requirements Status](https://requires.io/github/pythonsd/pythonsd-django/requirements.svg?branch=master)](https://requires.io/github/pythonsd/pythonsd-django/requirements/?branch=master)

Install requirements
```shell
pip install -r requirements/local.txt
```

Setup pre-commit hooks for style checking
```shell
pre-commit install
```

Compile SASS
```shell
invoke build
```

Create local database
```shell
./manage.py migrate
```

Add a superuser
```shell
./manage.py createsuperuser
```

Run local development server
```shell
./manage.py runserver
```

Run tests
```shell
tox
```
