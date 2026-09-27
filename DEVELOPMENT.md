# Local Development

## Tech stack

Django 5 and Django REST Framework on PostgreSQL (13+, with the `pg_trgm` extension), with Python dependencies managed by [`uv`](https://docs.astral.sh/uv/).

## Project layout

- `botc/` - Django project: settings, URLs, storage and WSGI/ASGI entry points.
- `scripts/` - the main app: models, views, filters, the REST API (`api/` routes), script JSON validation, templates, static files and management commands.
- `tests/` - pytest suite.
- `dev/` - Dockerfile/compose file for a local PostgreSQL database and `characters.json` fixture data.
- `.devcontainer/` - VS Code Dev Container configuration.

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
5. Start the development server: `uv run python manage.py runserver 0.0.0.0:8000`
6. Visit [http://localhost:8000](http://localhost:8000)

The dev container automatically:
- Sets up Python with `uv`
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

The site uses PostgreSQL as the backend database. The minimum PostgreSQL version required is v13. The PostgreSQL database must have the `postgresql-contrib` debian installed. It is recommended that you use [docker compose](./dev/docker-compose.yml) to spin up the [attached Dockerfile](./dev/Dockerfile) as your PostgreSQL database.

In order to test the "Name" and "Author" search fields, you must apply the following migration to your database once it has been deployed.

```python
from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):
    operations = [TrigramExtension()]
```

## Python environment

This project uses [`uv`](https://docs.astral.sh/uv/) to manage python dependencies. Follow the [Installing uv](https://docs.astral.sh/uv/getting-started/installation/) guide to install uv.

Python 3.13 or newer is required. You can then install the python environment using `uv sync`

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

`botc/local.py` is only used for development. The Azure deployment uses `botc/production.py`, which reads the settings below from environment variables.

| Setting | Effect |
| --- | --- |
| `UPLOAD_DISABLED` | Hides the upload form for everyone except staff. |
| `BANNER` | Text shown as a banner at the top of every page, or `None` for no banner. |
| `DISABLE_VALIDATORS` | Skips JSON validation of uploaded scripts (`scripts/validators.py`). Environment variable only, defaults to off. |
| `CORS_ALLOW_ALL_ORIGINS` | Allows cross-origin `GET` requests to `/api/`. Environment variable only, defaults to off. |

## Running and Migration

Per the usual Django development instructions, you need to apply the migrations to the database before running, create the static files and admin account. Run 

1. `uv run python manage.py migrate`
1. `uv run python manage.py collectstatic`
1. `uv run python manage.py createsuperuser`

You can also populate the database with all the characters (this is useful for testing some function), but you will need to upload your own scripts (some script data may come at a later date)

`uv run python manage.py loaddata dev/characters`

The site can be run using:

`uv run python manage.py runserver 0.0.0.0:8000`

The site will be accessible at `http://localhost:8000`. You can access the Django admin panel, logging in with the credentials you used to create the super user at `http://localhost:8000/admin`

## Live Debugging

If you use VSCode for as your IDE, you can use the following `settings.json` to launch the website in debug mode so that you can step through code

```json
{
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

## Testing

Tests use [pytest](https://docs.pytest.org/) with the settings in `tests/settings.py`. Because the models depend on PostgreSQL features (`GinIndex`, `pg_trgm`), the tests need a running PostgreSQL database. The defaults match the CI service (`postgres`/`postgres` on `localhost:5432`) and can be overridden with the `TEST_DB_NAME`, `TEST_DB_HOST`, `TEST_DB_PORT`, `TEST_DB_USER` and `TEST_DB_PASSWORD` environment variables.

`uv run pytest tests/`

CI runs both ruff and pytest on every push and pull request.

## Management commands

Maintenance commands in `scripts/management/commands/`, run with `uv run python manage.py <command>`. They are safe to re-run, but back up the database before running them against production data.

| Command | Purpose |
| --- | --- |
| `update_script_counts` | Recalculates the per-type character counts (Townsfolk, Outsiders, etc.) on every script version from its stored JSON. |
| `update_homebrewiness` | Recalculates whether each script version is official, hybrid or homebrew, and syncs the Hybrid and Homebrew tags. The tags are looked up by hard-coded IDs (49 and 50) in the command, so update those if your database differs. |
| `fix_latest_flags` | Ensures only the highest version of each script has `latest=True`. |
| `delete_orphaned_scripts` | Lists and deletes scripts that have no versions. This deletes data without asking for confirmation. |
