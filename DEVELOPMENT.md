# Local Development

## Quick Start with Dev Containers

VS Code Dev Containers provides a fully configured development environment with all dependencies pre-installed.

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Getting Started
1. Open this repository in VS Code
2. When prompted, click "Reopen in Container" (or press `F1` and select "Dev Containers: Reopen in Container")
3. Wait for the container to build and set up (first time takes a few minutes)
4. Once ready, create a superuser: `uv run python manage.py createsuperuser`
5. Start the development server: `uv run python manage.py runserver`
6. Visit [http://localhost:8000](http://localhost:8000)

The dev container automatically:
- Sets up Python 3.12 with `uv`
- Installs all dependencies
- Configures PostgreSQL with the required extensions
- Runs database migrations
- Loads character data
- Configures Django settings
- Installs helpful VS Code extensions

### Debugging in Dev Container
The container is pre-configured for debugging. Press `F5` or use the "Run and Debug" panel in VS Code to start the Django server in debug mode with breakpoints enabled.

## Manual Local Development

If you prefer not to use Dev Containers, you can set up the environment manually.

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

This project uses [`uv`](https://docs.astral.sh/uv/) to manage python dependencies. Follow the [Installing uv](https://docs.astral.sh/uv/getting-started/installation/) guide to install uv.

You can then install python environment using `uv sync`

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

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
BS_ICONS_CACHE = os.path.join(STATIC_ROOT, "icon_cache")
DEBUG = True

UPLOAD_DISABLED = False
BANNER = None

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

```

Be sure to choose your own random string for the `SECRET_KEY`. [You can generate one here](https://randomkeygen.com/). 

If you are not using the docker compose PostgreSQL database then you'll need to configure the `DATABASES` entry above with your own credentials.

## Running and Migration

Per the usual Django development instructions, you need to apply the migrations to the database before running, create the static files and admin account. Run 

1. `uv run python manage.py migrate`
1. `uv run python manage.py collectstatic`
1. `uv run python manage.py createsuperuser`

You can also populate the database with all the characters (this is useful for testing some function), but you will need to upload your own scripts (some script data may come at a later date)

`uv run python manage.py loaddata dev/characters`

The site can be run using:

`uv run python manage.py runserver`

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

## Linting

This project uses [Ruff](https://docs.astral.sh/ruff/#ruff) for linting. The GitHub workflow includes a lint using ruff, but before submitting any code for review, please ensure that ruff passes by running `uv run ruff check`