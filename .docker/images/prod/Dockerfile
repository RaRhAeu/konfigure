FROM python:3.9.4-slim

ARG USERNAME=appuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG WORKDIR=/app

WORKDIR $WORKDIR

RUN apt update && apt install -y curl \
    && rm -rf /var/lib/apt/lists/*

RUN adduser -u $USER_UID --disabled-password --gecos "" $USERNAME && chown -R $USERNAME $WORKDIR
USER $USERNAME
ENV PATH $PATH:/home/$USERNAME/.local/bin
ENV POETRY_VERSION 1.1.15
RUN pip install --user -U pip
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3 -

RUN poetry config virtualenvs.create false

COPY ./alembic.ini ./
COPY ./poetry.lock ./pyproject.toml ./

COPY ./migrations ./migrations
COPY ./app ./app

RUN poetry install --no-dev

EXPOSE 8000

CMD ["uvicorn", "app.asgi:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop", "--http", "h11", "--log-level", "info"]
