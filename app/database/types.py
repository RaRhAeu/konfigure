import binascii
import uuid
import warnings
from typing import Any, Optional, Type

import orjson
import pydantic
import sqlalchemy as sa
from cryptography.fernet import Fernet
from pydantic import BaseModel
from pydantic.json import pydantic_encoder
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.functions import FunctionElement
from sqlalchemy.types import CHAR, TypeDecorator, TypeEngine

from app.settings import settings


class GenerateUUID(FunctionElement):
    """
    Platform-independent UUID default generator.
    Note the actual functionality for this class is specified in the
    `compiles`-decorated functions below
    """

    name = "uuid_default"


@compiles(GenerateUUID, "postgresql")
@compiles(GenerateUUID)
def _generate_uuid_postgresql(element, compiler, **kwargs):
    """
    Generates a random UUID in Postgres; requires the pgcrypto extension.
    """

    return "(GEN_RANDOM_UUID())"


@compiles(GenerateUUID, "sqlite")
def _generate_uuid_sqlite(element, compiler, **kwargs):
    """
    Generates a random UUID in other databases (SQLite) by concatenating
    bytes in a way that approximates a UUID hex representation. This is
    sufficient for our purposes of having a random client-generated ID
    that is compatible with a UUID spec.
    """

    return """
    (
        lower(hex(randomblob(4)))
        || '-'
        || lower(hex(randomblob(2)))
        || '-4'
        || substr(lower(hex(randomblob(2))),2)
        || '-'
        || substr('89ab',abs(random()) % 4 + 1, 1)
        || substr(lower(hex(randomblob(2))),2)
        || '-'
        || lower(hex(randomblob(6)))
    )
    """


class UUID(TypeDecorator):
    """
    Platform-independent UUID type.
    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(36), storing as stringified hex values with
    hyphens.
    """

    impl = TypeEngine
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        elif dialect.name == "postgresql":
            return str(value)
        elif isinstance(value, uuid.UUID):
            return str(value)
        else:
            return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class AESField(TypeDecorator):

    impl = sa.Text
    cache_ok = True

    _cipher = Fernet(key=settings.AES_KEY)

    def process_bind_param(self, value: Any, dialect: str) -> Optional[str]:
        if value is None:
            return value
        if isinstance(value, str):
            value = value.encode("utf-8")
        else:
            value = orjson.dumps(value, default=pydantic_encoder)
        assert isinstance(value, bytes)
        value = self._cipher.encrypt(value).decode("utf-8")
        return value

    def process_result_value(self, value: Any, dialect: str) -> Optional[str]:
        if value is None:
            return value
        try:
            if isinstance(value, str):
                value = self._cipher.decrypt(value.encode("utf-8")).decode("utf-8")
                return orjson.loads(value)
        except (UnicodeDecodeError, binascii.Error):
            warnings.warn("Improperly encrypted field in db found")
        return value


class JSON(TypeDecorator):
    """
    JSON type that returns SQLAlchemy's dialect-specific JSON types, where
    possible. Uses generic JSON otherwise.
    The "base" type is postgresql.JSONB to expose useful methods prior
    to SQL compilation
    """

    impl = postgresql.JSONB
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.JSONB(none_as_null=True))
        elif dialect.name == "sqlite":
            return dialect.type_descriptor(sqlite.JSON(none_as_null=True))
        else:
            return dialect.type_descriptor(sa.JSON(none_as_null=True))

    def process_bind_param(self, value, dialect):
        """Prepares the given value to be used as a JSON field in a parameter binding"""
        return value


class Pydantic(TypeDecorator):
    """
    A pydantic type that converts inserted parameters to
    json and converts read values to the pydantic type.
    """

    impl = JSON
    cache_ok = True

    def __init__(
        self,
        pydantic_type: Type[BaseModel],
        sa_column_type=None,
        validate: bool = False,
    ):
        super().__init__()
        self._pydantic_type = pydantic_type
        self._validate = validate
        if sa_column_type is not None:
            self.impl = sa_column_type

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if self._validate:
            value = pydantic.parse_obj_as(self._pydantic_type, value)
        return value.dict(exclude_none=True)

    def process_result_value(self, value, dialect):
        if value is not None:
            # load the json object into a fully hydrated typed object
            return pydantic.parse_obj_as(self._pydantic_type, value)
