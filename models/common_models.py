from abc import ABC
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Column, Field, DateTime, func, TEXT, Relationship, UniqueConstraint, text, Integer
from sqlalchemy.orm import declared_attr
from pydantic.fields import PrivateAttr


nowtz = text('CURRENT_TIMESTAMP')


class UpdatedAtMixin:
    @declared_attr
    def updated_at(cls):  # noqa
        return Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)


class CreatedAtMixin:
    @declared_attr
    def created_at(cls):  # noqa
        return Column(DateTime(timezone=True), server_default=func.now(), nullable=True)


class DTMixin(UpdatedAtMixin, CreatedAtMixin):
    pass


class IntPkMixin:
    id: int | None = Field(primary_key=True, nullable=False)


class UUIDPkMixin:
    id: UUID | None = Field(primary_key=True, nullable=False, default_factory=uuid4)


class MetaMixin:
    _is_cache: bool = PrivateAttr(default=False)


    @property
    def is_cache(self):
        return self._is_cache


    @is_cache.setter
    def is_cache(self, value: bool):
        self._is_cache = value


class TaxonomyMod(IntPkMixin, DTMixin, ABC):
    name: str = Field(max_length=199)
    slug: str = Field(max_length=199)
    parent_id: int | None = Field(default=None, foreign_key='app_taxonomy.id')
    type: str = Field(default='category', index=True)
    is_active: bool = Field(default=True)
    account_id: int | None = Field(default=None, foreign_key='auth_account.id', ondelete='CASCADE')


class Taxonomy(TaxonomyMod, SQLModel, table=True):
    __tablename__ = 'app_taxonomy'
    __table_args__ = (UniqueConstraint('name', 'parent_id', 'account_id'),)
    parent: 'Taxonomy' = Relationship(back_populates='children',
                                         sa_relationship_kwargs={'remote_side': '[Taxonomy.id]'})
    children: list['Taxonomy'] = Relationship(back_populates='parent')
    account: 'Account' = Relationship(back_populates='taxonomies')  # noqa


    def __repr__(self) -> str:
        return f'<Taxonomy {self.id}: {self.name}>'


class OptionMod(IntPkMixin, DTMixin, SQLModel, table=True):
    __tablename__ = 'app_option'
    __table_args__ = (UniqueConstraint('name', 'owner_id'),)
    name: str = Field(max_length=50)
    value: str = Field(sa_column=Column(TEXT, default='', server_default=''))
    type: int | None = Field(default=2, sa_column=Column(Integer, server_default='2'))
    description: str | None = Field(sa_column=Column(TEXT, default='', server_default=''))
    owner_id: int | None = Field(foreign_key='auth_account.id', default=None, ondelete='CASCADE',
                                 sa_column_kwargs={'server_default': text('NULL')})
    # --
    owner: 'Account' = Relationship(back_populates='options_rel')  # noqa


    def __repr__(self) -> str:
        return f'<Option {self.id}: {self.name}>'  # noqa
