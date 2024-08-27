#syntax:docker/dockerfile:1.7-labs

FROM python:alpine3.19

ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.3

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir poetry==$POETRY_VERSION
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

COPY exclude=*.lock exclude=*.toml . ./

EXPOSE 8000

RUN ["python", "manage.py", "makemigrations"]
RUN ["python", "manage.py", "migrate"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]