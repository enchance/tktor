from typing import TYPE_CHECKING
from abc import ABC
from sqlmodel import (SQLModel, Field, Column, String, text, Relationship, Text, Boolean, DateTime, func)
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

from . import modstr
from .common_models import IntPkMixin, DTMixin, MetaMixin, UpdatedAtMixin


if TYPE_CHECKING:
    from authentication import Account


class Ban(IntPkMixin, UpdatedAtMixin, SQLModel, table=True):
    __tablename__ = 'auth_ban'
    account_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE')
    implementor_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE')
    notes: str = Field(sa_column=Column(Text, default='', server_default=''))
    is_active: bool = Field(default=True)
    banned_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=True))
    # --
    account: 'Account' = Relationship(
        back_populates='bans_received', sa_relationship_kwargs={'foreign_keys': '[Ban.account_id]'})
    implementor: 'Account' = Relationship(
        back_populates='bans_implemented', sa_relationship_kwargs={'foreign_keys': '[Ban.implementor_id]'})


    def __str__(self):
        return modstr(self, 'account_id', 'is_active')


class Address(IntPkMixin, DTMixin, SQLModel, table=True):
    __tablename__ = 'auth_address'
    address1: str = Field(max_length=199, default='')
    address2: str = Field(max_length=199, default='')
    city: str = Field(max_length=199, default='')
    zip: str = Field(max_length=199, default='')
    account_id: int | None = Field(foreign_key='auth_account.id', ondelete='CASCADE')
    # --
    account: 'Account' = Relationship(back_populates='addresses')


class Profile(SQLModel, table=True):
    __tablename__ = 'auth_profile'
    id: int | None = Field(primary_key=True, foreign_key='auth_account.id', unique=True, ondelete='CASCADE')
    firstname: str = Field(sa_column=Column(Text, default='', server_default=''))
    middlename: str = Field(sa_column=Column(Text, default='', server_default=''))
    lastname: str = Field(sa_column=Column(Text, default='', server_default=''))
    mobile: list[str] = Field(sa_column=Column(ARRAY(String), server_default='{}'), default_factory=list)
    telephone: list[str] = Field(sa_column=Column(ARRAY(String), server_default='{}'), default_factory=list)
    gender: str = Field(sa_column=Column(String(50), default='', server_default=''))
    meta: dict = Field(sa_column=Column(JSONB, server_default=text("'{}'::jsonb")), default_factory=dict)
    # --
    account: 'Account' = Relationship(back_populates='profile')


    @property
    def fullname(self) -> str:
        fullname = f'{self.firstname} {self.middlename} {self.lastname}'
        return ' '.join(fullname.split())


class AccountMod(MetaMixin, IntPkMixin, DTMixin, ABC):
    uid: str = Field(unique=True, nullable=True)
    email: str = Field(max_length=199, unique=True)
    username: str = Field(sa_column=Column(String(199), unique=True, nullable=True))
    display: str = Field(sa_column=Column(String(199), default='', server_default=''))
    avatar: str = Field(sa_column=Column(Text, default='', server_default=''))
    roles: list[str] | None = Field(sa_column=Column(ARRAY(String), server_default='{}'), default_factory=list)
    custom_permissions: list[str] | None = Field(sa_column=Column(ARRAY(String), server_default='{}'),
                                                 default_factory=list)
    is_banned: bool = Field(default=False)
    is_verified: bool = Field(default=False)


class RoleMod(MetaMixin, DTMixin, ABC):
    name: str = Field(max_length=20, primary_key=True)
    permissions: set[str] = Field(default_factory=set, sa_column=Column(ARRAY(String(199)), server_default='{}'))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, index=True, server_default='TRUE'))
