from typing import TYPE_CHECKING
from abc import ABC
from datetime import datetime
from sqlmodel import (SQLModel, Field, Column, String, text, Relationship, Text, Boolean,
                      DateTime, UniqueConstraint)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

from .common_models import IntPkMixin, DTMixin, MetaMixin


if TYPE_CHECKING:
    from auth import Account


class BanMod(IntPkMixin, DTMixin, SQLModel, table=True):
    __tablename__ = 'auth_ban'
    recipient_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE')
    owner_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE')
    notes: str = Field(sa_column=Column(Text, default='', server_default=''))
    is_active: bool = Field(default=True)
    # --
    account: 'Account' = Relationship(
        back_populates='bans', sa_relationship_kwargs={'foreign_keys': '[BanMod.recipient_id]'})
    banner: 'Account' = Relationship(
        back_populates='ban_owners', sa_relationship_kwargs={'foreign_keys': '[BanMod.owner_id]'})


class AddressMod(IntPkMixin, DTMixin, SQLModel, table=True):
    __tablename__ = 'auth_address'
    address1: str = Field(max_length=199, default='')
    address2: str = Field(max_length=199, default='')
    city: str = Field(max_length=199, default='')
    zip: str = Field(max_length=199, default='')
    owner_id: int | None = Field(foreign_key='auth_account.id', ondelete='CASCADE')
    # --
    account: 'Account' = Relationship(back_populates='addresses')


class ProfileMod(SQLModel, table=True):
    __tablename__ = 'auth_profile'
    id: int | None = Field(primary_key=True, foreign_key='auth_account.id', ondelete='CASCADE')
    firstname: str = Field(sa_column=Column(Text, default='', server_default=''))
    middlename: str = Field(sa_column=Column(Text, default='', server_default=''))
    lastname: str = Field(sa_column=Column(Text, default='', server_default=''))
    mobile: list[str] = Field(sa_column=Column(ARRAY(String), server_default='{}'), default_factory=list)
    telephone: list[str] = Field(sa_column=Column(ARRAY(String), server_default='{}'), default_factory=list)
    gender: str = Field(sa_column=Column(String(20), default='', server_default=''))
    meta: dict = Field(sa_column=Column(JSONB, server_default=text("'{}'::jsonb")), default_factory=dict)
    # --
    account: 'Account' = Relationship(back_populates='profile')


class AccountMod(MetaMixin, IntPkMixin, DTMixin, ABC):
    uid: str = Field(unique=True, nullable=True)
    email: str = Field(max_length=199)
    username: str = Field(sa_column=Column(String(199), unique=True, nullable=True))
    display: str = Field(sa_column=Column(String(199), default='', server_default=''))
    avatar: str = Field(sa_column=Column(Text, default='', server_default=''))
    roles: list[str] | None = Field(sa_column=Column(ARRAY(String), server_default='{}'), default_factory=list)
    custom_permissions: list[str] | None = Field(sa_column=Column(ARRAY(String), server_default='{}'),
                                                 default_factory=list)
    is_banned: bool = Field(default=False)
    is_verified: bool = Field(default=False)
