# SDPUG Django Site

Install requirements
```shell
pip install -r requirements/local.txt
```

Compile SASS
```shell
make compile-sass
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
