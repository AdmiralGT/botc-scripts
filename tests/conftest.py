import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import requests
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db import connection

from scripts import models
from scripts.views import calculate_edition, count_character
from tests.samples import TROUBLE_BREWING

CHARACTERS_FIXTURE = Path(__file__).resolve().parent.parent / "dev" / "characters.json"


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        call_command("loaddata", CHARACTERS_FIXTURE, verbosity=0)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def fake_get(url, *args, **kwargs):
        if url.endswith("roles.json"):
            return SimpleNamespace(ok=True, content=b"[]")
        raise requests.exceptions.Timeout(url)

    monkeypatch.setattr(requests, "get", fake_get)


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user("alice", "alice@example.com", "password")


@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create_user("bob", "bob@example.com", "password")


@pytest.fixture
def make_script(db):
    def _make_script(name="Trouble Brewing", version="1", content=None, owner=None, author="Author", **fields):
        content = content if content is not None else TROUBLE_BREWING
        script, _ = models.Script.objects.get_or_create(name=name, defaults={"owner": owner})
        return models.ScriptVersion.objects.create(
            script=script,
            version=version,
            content=content,
            author=author,
            num_townsfolk=count_character(content, models.CharacterType.TOWNSFOLK),
            num_outsiders=count_character(content, models.CharacterType.OUTSIDER),
            num_minions=count_character(content, models.CharacterType.MINION),
            num_demons=count_character(content, models.CharacterType.DEMON),
            num_fabled=count_character(content, models.CharacterType.FABLED),
            num_loric=count_character(content, models.CharacterType.LORIC),
            num_travellers=count_character(content, models.CharacterType.TRAVELLER),
            edition=calculate_edition(content),
            **fields,
        )

    return _make_script


@pytest.fixture
def upload(client):
    def _upload(name="Trouble Brewing", content=None, version="1", author="", **extra):
        content = content if content is not None else TROUBLE_BREWING
        data = {
            "name": name,
            "author": author,
            "script_type": models.ScriptTypes.FULL,
            "version": version,
            "content": SimpleUploadedFile("script.json", json.dumps(content).encode(), "application/json"),
            **extra,
        }
        return client.post("/script/upload", data)

    return _upload
