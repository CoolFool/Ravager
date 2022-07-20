#Template from https://github.com/michaeloliverx/python-poetry-docker-example/blob/master/docker/Dockerfile
FROM python:3.10-slim-buster as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


# builder-base is used to build dependencies
FROM python-base as builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
ENV POETRY_VERSION=1.1.12
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

# We copy our Python requirements here to cache them
# and install only runtime deps using poetry
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev  # respects

FROM python-base as production
RUN apt-get update \
  && apt-get install --no-install-recommends -y aria2 curl \
  && apt-get clean \
  && apt-get autoremove \
  && rm -rf /var/lib/apt/lists/*  \
  && rm -rf /tmp/*
COPY --from=builder-base $VENV_PATH $VENV_PATH
COPY ./ravager /app/ravager
COPY start.sh /app
COPY healthcheck.sh /app
WORKDIR /app
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV HEROKU_APP="false"
HEALTHCHECK --interval=1m --timeout=3s CMD ["/app/healthcheck.sh"]
CMD ["./start.sh"]
