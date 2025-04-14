from abc import ABC
from uuid import UUID, uuid4
from slugify import slugify
from sqlmodel import SQLModel, Column, Field, DateTime, func, TEXT, Relationship, UniqueConstraint, text, Integer
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import declared_attr
from pydantic.fields import PrivateAttr

from .utils import modstr


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


class Taxonomy(IntPkMixin, DTMixin, SQLModel, table=True):
    __tablename__ = 'app_taxonomy'
    __table_args__ = (
        UniqueConstraint('name', 'parent_id', 'account_id', name='unique_name_parent'),
        UniqueConstraint('slug', 'account_id', name='unique_slug'),
    )
    name: str = Field(max_length=199)
    slug: str | None = Field(max_length=199, default='')
    parent_id: int | None = Field(default=None, foreign_key='app_taxonomy.id', ondelete='SET NULL')
    type: str = Field(default='category', index=True)
    is_active: bool = Field(default=True)
    account_id: int | None = Field(default=None, foreign_key='auth_account.id', ondelete='CASCADE')
    # --
    parent: 'Taxonomy' = Relationship(back_populates='children',
                                      sa_relationship_kwargs={'remote_side': 'Taxonomy.id'})
    children: list['Taxonomy'] = Relationship(back_populates='parent')
    account: 'Account' = Relationship(back_populates='taxonomies')  # noqa


    def __str__(self) -> str:
        return modstr(self, 'name')


    def __init__(self, **kwargs):
        slug_text = kwargs.get('slug', kwargs['name']) or kwargs['name']
        kwargs['slug'] = slugify(slug_text, entities=False)
        super().__init__(**kwargs)


    async def add_child(self, tax: 'Taxonomy', *, session: AsyncSession):
        await session.refresh(self, ['children'])
        self.children.append(tax)
        await session.commit()
        tax.parent = self


class Option(IntPkMixin, DTMixin, SQLModel, table=True):
    __tablename__ = 'app_option'
    __table_args__ = (UniqueConstraint('name', 'account_id', name='unique_name'),)
    name: str = Field(max_length=50)
    value: str = Field(sa_column=Column(TEXT, default='', server_default=''))
    type: int | None = Field(default=2, sa_column=Column(Integer, server_default='2'))
    description: str | None = Field(sa_column=Column(TEXT, default='', server_default=''))
    account_id: int | None = Field(foreign_key='auth_account.id', default=None, ondelete='CASCADE',
                                   sa_column_kwargs={'server_default': text('NULL')})
    # --
    account: 'Account' = Relationship(back_populates='options_rel')  # noqa


    def __str__(self) -> str:
        return modstr(self, 'type', 'name')
