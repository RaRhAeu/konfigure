FROM python:3.9.4-slim

# RUN apt update && apt install -y gcc

RUN pip install --user -U pip
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
RUN poetry config virtualenvs.create false

COPY ./alembic.ini /
COPY ./poetry.lock ./pyproject.toml /

RUN poetry install --no-root

COPY ./migrations /migrations
COPY ./app /app

EXPOSE 8000

CMD ["uvicorn", "muninn.asgi:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop", "--http", "h11", "--log-level", "info"]
