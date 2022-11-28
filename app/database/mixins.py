import sqlalchemy as sa
from sqlalchemy import FetchedValue
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import declarative_mixin, declared_attr

from app.database.types import JSON, UUID, GenerateUUID


@declarative_mixin
class IdModelMixin:
    @declared_attr
    def id(cls):
        return sa.Column(UUID(), primary_key=True, server_default=GenerateUUID())


@declarative_mixin
class CreatedUpdatedMixin:
    @declared_attr
    def created_at(cls):
        return sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return sa.Column(
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
            server_onupdate=FetchedValue(),
        )


@declarative_mixin
class SpecMixin:
    @declared_attr
    def spec(cls):
        return sa.Column(JSON())


@declarative_mixin
class NamespacedMixin:
    @declared_attr
    def namespace(cls):
        return sa.Column(
            sa.Unicode(255), sa.ForeignKey("namespace.name", ondelete="CASCADE")
        )


@declarative_mixin
class SoftDeleteMixin:
    @declared_attr
    def tombstone(cls):
        return sa.Column(sa.Boolean(), default=False)

    @hybrid_property
    def not_deleted(self):
        return not self.tombstone

    @not_deleted.expression
    def not_deleted(cls):
        return cls.tombstone.is_(False)


class LabelAnnotationMixin:
    @declared_attr
    def labels(cls):
        return sa.Column(JSON(), default={})

    @declared_attr
    def annotations(cls):
        return sa.Column(JSON(), default={})


class MetadataMixin(LabelAnnotationMixin, CreatedUpdatedMixin):
    pass
