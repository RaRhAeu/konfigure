import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from app.database.mixins import IdModelMixin, MetadataMixin, NamespacedMixin
from app.database.orm import ORMModel
from app.database.types import JSON, AESField

Base = declarative_base(cls=ORMModel)


class Namespace(Base, IdModelMixin, MetadataMixin):
    __tablename__ = "namespace"
    name = sa.Column(sa.Unicode(255), unique=True)
    resource_version = sa.Column(sa.Integer(), default=1)


class ConfigurationDefinition(Base, IdModelMixin, MetadataMixin):
    __tablename__ = "configuration_definition"

    spec = sa.Column(JSON(), nullable=True)


class Configuration(Base, IdModelMixin, NamespacedMixin):
    __tablename__ = "configuration"
    __table_args__ = (
        sa.UniqueConstraint("namespace", "kind", "name", name="uq_ns_kind_name"),
    )
    api_group = sa.Column(sa.Unicode(255))
    version = sa.Column(sa.Unicode(255))

    kind = sa.Column(sa.Unicode(255))
    name = sa.Column(sa.Unicode(255))
    resource_version = sa.Column(sa.Integer(), default=1)
    spec = sa.Column(JSON(), nullable=True)
    status = sa.Column(JSON(), nullable=True)
    subresources = sa.Column(JSON(), default={})

    @hybrid_property
    def api_version(self):
        return f"{self.api_group}/{self.version}"

    @api_version.setter
    def api_version(self, value: str):
        self.api_group, _, self.version = value.partition("/")


class Secret(Base, IdModelMixin, NamespacedMixin):
    __tablename__ = "secret"

    resource_version = sa.Column(sa.Integer(), default=1)
    data = sa.Column(AESField())
