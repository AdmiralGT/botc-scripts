FROM python:3.10.5-slim

RUN pip install "poetry==1.1.3"

WORKDIR /usr/local/app
COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY manage.py ./
COPY ./botc ./botc
COPY ./scripts ./scripts
