FROM mirror.gcr.io/python:3.10-slim as build-im

ENV PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_VERSION=1.8.3

RUN apt-get update && apt-get upgrade -y \
  && apt-get install -y openssh-client \
  && apt-get install -y --no-install-recommends build-essential \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/* \
  # Upgrade pip:
  && pip install --upgrade pip setuptools \
  # Installing poetry with pip:
  && pip install poetry==$POETRY_VERSION \
  && rm -rf /home/root/.cache/*

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock ./

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi


FROM mirror.gcr.io/python:3.10-slim
RUN apt update && apt install -y --no-install-recommends make gettext libffi-dev && rm -rf /var/lib/apt/lists/*

COPY --from=build-im /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=build-im /usr/local/src/ /usr/local/src/
COPY --from=build-im /usr/local/bin/ /usr/local/bin/

WORKDIR /app
COPY ./sources .

EXPOSE 8200
