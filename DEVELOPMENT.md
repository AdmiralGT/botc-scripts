# Local Development

## Database

The site uses PostgreSQL as the backend database. The mimimum PostgreSQL version required in v13. The PostgreSQL database must have the `postgresql-contrib` debian installed. It is recommended that you use [docker compose](./dev/docker-compose.yml) to spin up the [attached Dockerfile](./dev/Dockerfile) as your PostgreSQL database.

In order to test the "Name" and "Author" search fields, you must apply the following migration to your database once it has been deployed.

```python
from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations

class Migration(migrations.Migration):
    operations = [
        TrigramExtension()
    ]
```

## Python environment

This project uses `poetry` to manage python dependencies. Follow the [Poetry installation instructions](https://python-poetry.org/docs/#installation) to install poetry.

Note: Users have reported getting stuck in the install, running `export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring` may fix this.

You can then install python environment using `poetry install`

### Creating the Config

By default, `manage.py` looks for the file `botc/local.py`. You must create a `botc/local.py` with the following content:

```python
from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "HOST": "localhost",
        "USER": "postgres@db",
        "PASSWORD": "postgres",
    }
}

SECRET_KEY = "<random_string>"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
BS_ICONS_CACHE = os.path.join(STATIC_ROOT, "icon_cache")
DEBUG = True

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

```

Be sure to choose your own random string for the `SECRET_KEY`. [You can generate one here](https://randomkeygen.com/). 

If you are not using the docker compose PostgreSQL database then you'll need to configure the `DATABASES` entry above with your own credentials.

## Running and Migration

Per the usual Django development instructions, you need to apply the migrations to the database before running, create the static files and admin account. Run 

1. `poetry run python manage.py migrate`
1. `poetry run python manage.py collectstatic`
1. `poetry run python manage.py createsuperuser`

You can also populate the database with all the characters (this is useful for testing some function), but you will need to upload your own scripts (some script data may come at a later date)

`poetry run python manage.py loaddata dev/characters`

The site can be run using:

`poetry run python manage.py runserver`

The site will be accessible at `http://localhost:8000`. You can access the Django admin panel, logging in with the credentials you used to create the super user at `http://localhost:8000/admin`

## Live Debugging

If you use VSCode for as your IDE, you can use the following `settings.json` to launch the website in debug mode so that you can step through code

```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "justMyCode": false,
            "name": "Python: Django",
            "type": "python",
            "request": "launch",
            "program": "manage.py",
            "args": [
                "runserver"
            ],
            "django": true
        }
    ]
}
```