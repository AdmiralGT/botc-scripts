# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, Cursor, etc.) working in this repo.

## What this is

Django 5.2 web app + REST API hosting Blood on the Clocktower (BotC) custom scripts — JSONs from official Script Tool. Users upload script JSONs (optional PDF), browse/filter/search, vote, favourite, comment, group into collections. Single Django app `scripts` in package `botc`. Python 3.13, deps via `uv`, PostgreSQL backend.

## Commands

Python commands run via `uv run`.

```bash
uv sync --all-extras --dev                          # install deps (incl. dev group)

uv run python manage.py migrate
uv run python manage.py collectstatic
uv run python manage.py createsuperuser
uv run python manage.py loaddata dev/characters     # populate official characters
uv run python manage.py runserver 0.0.0.0:8000

uv run ruff check                                    # lint (CI gate)
uv run ruff format --check                           # format check (CI gate)
uv run ruff format                                   # apply formatting

uv run pytest tests/ --cov scripts                  # full test suite
uv run pytest tests/test_similarity.py              # one file
uv run pytest tests/test_similarity.py::test_same   # one test
```

Ruff config (`pyproject.toml`): line-length 120, `RUF012` ignored, excludes `scripts/migrations`, `botc/`, `manage.py`.

## Settings layout (important)

No single settings file — module chosen per context:

- `botc/settings.py` — base config; others import via `from .settings import *`.
- `botc/local.py` — **local dev; gitignored, you must create it.** `manage.py` defaults `DJANGO_SETTINGS_MODULE` to `botc.local` (override with `DJANGO_SETTINGS` env var). Template + required keys in `DEVELOPMENT.md`.
- `botc/production.py` — Azure prod (env-var driven: Postgres, Azure blob storage, OAuth secrets, gunicorn).
- `tests/settings.py` — used by pytest (`DJANGO_SETTINGS_MODULE = tests.settings` in `pyproject.toml`). Intentionally **empty**: current tests exercise only pure functions in `scripts/script_json.py` (no DB, no Django app loading), so no settings needed. ORM-touching tests would need this file populated.

## Database requirement

PostgreSQL 13+ mandatory — app uses Postgres-only features, won't run on SQLite despite `db.sqlite3` gitignore entry:
- `JSONField` `content__contains` lookups (statistics, character filtering)
- `TrigramSimilarity` for name/author search — needs `pg_trgm` extension. **Not** in migrations by default; add `TrigramExtension()` migration manually (see `DEVELOPMENT.md`).
- `.distinct("language")` (DISTINCT ON)

## Architecture

### Data model (`scripts/models.py`)
- **`Script`** — named script; owns many **`ScriptVersion`** (`related_name="versions"`). `latest_version()` = highest `version`.
- **`ScriptVersion`** — the real unit. Holds uploaded JSON in `content` (source of truth), plus `pdf`, `version` (`VersionField`), and **derived** metadata: `num_townsfolk/outsiders/minions/demons/fabled/loric/travellers`, `edition`, `homebrewiness`, and `latest` boolean flagging newest version per `Script`. `tags` is M2M to `ScriptTag`.
- **`ScriptViewManager`** — default `objects` manager, annotates every queryset with `score` (vote count) + `num_favs`. `plain_objects` is raw unannotated manager — use when you don't want aggregate joins.
- Interaction models (`Comment`, `Vote`, `Favourite`) FK to `Script` via `parent`; `Vote`/`Favourite` unique per `(parent, user)`. `Collection` is M2M of `ScriptVersion`.
- Characters: `ClocktowerCharacter` (official, from `dev/characters.json`), `HomebrewCharacter` (per-script, `script` FK), `Translation` — all extend abstract `BaseCharacter`/`BaseCharacterInfo`. `full_character_json()` rebuilds a Script-Tool-shaped character dict; official images resolve to external GitHub repo (`tomozbot/botc-icons`) unless homebrew `image_url` set.
- `Edition` is `IntegerChoices`. New edition requires updating upload view (noted in comment on enum).

### Upload pipeline — shared between web and API
Uploaded JSON parsed; all `num_*`, `edition`, `homebrewiness` fields **derived at upload time** by helpers in `scripts/views.py`:
`count_character`, `calculate_edition`, `create_characters_and_determine_homebrew_status`, `translate_json_content`.
**Two upload paths** call these same helpers — keep in sync when changing derivation logic:
- Web form: `views.ScriptUploadView` / `BaseScriptUploadView`.
- REST API: `viewsets.VersionViewSet.create` (imports helpers from `views.py`).
Homebrew status (`CLOCKTOWER`/`HYBRID`/`HOMEBREW`) auto-applies "Hybrid Script"/"Homebrew Script" tags. `latest` flag maintained on upload + delete (promotes next version, or deletes `Script` when last version goes).

### Pure JSON logic (`scripts/script_json.py`) — the tested core
No DB access. Handles: parsing/validation (`get_json_content`), legacy-format conversion (`revert_to_old_format`: bare-string entries → `{"id": ...}`), `strip_special_characters`, similarity scoring (`get_similarity`, teensyville vs full aware), upload-diffing (`get_json_additions`/`get_json_changes`), `compress_json` (gzip → base64 → urlencode, for shareable links). `tests/` targets these using fixtures in `tests/input/`.

### API (`scripts/urls.py`, `viewsets.py`, `api_views.py`, `serializers.py`)
DRF router under `/api/`: `scripts` (`VersionViewSet`, writable), `script_ids` (`ScriptViewSet`, read-only), `collections`. Plus function/`APIView` endpoints: `/api/characters`, `/api/statistics`, translation/translate routes. Reads open (anon read-only); writes require custom `scripts.api_write_permission` + `BasicAuthentication`. Schema via `drf-spectacular`; filtering via `django-filter` (`scripts/filters.py`). CORS GET-only, restricted to `/api/`.

### Web layer
Class-based views in `scripts/views.py` (~1400 lines) with `django-tables2` (`tables.py`) + `django-filter` (`filters.py`). Templates in `scripts/templates/`, custom tags in `scripts/templatetags/botc_script_tags.py`; `scripts/context_processors.custom_configuration` injects `BANNER` / `UPLOAD_DISABLED` into every template. Auth is `django-allauth` (email-based) with Google + Discord social login.

### Caching (`scripts/cache.py`)
`LocMemCache`. Caches official/homebrew character dicts (1h) and stashes advanced-search result PK lists (5min) so results page can page over them.

### Deployment
Azure App Service. `botc/production.py` drives everything from env vars; static/media to Azure Blob (`botc/storage.py`); served by gunicorn (`gunicorn.conf.py`). Workflows in `.github/workflows/` (`main_*` prod, `staging_*` staging; `pytest.yml` + `linter.yml` gate PRs). Local dev easiest via Dev Container (`.devcontainer/`), which provisions Postgres + runs setup automatically — see `DEVELOPMENT.md`.
