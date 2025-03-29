from sqlmodel import SQLModel, Relationship

from models.auth_models import ProfileMod, AccountMod, AddressMod, BanMod
from models.common_models import OptionMod


class Account(AccountMod, SQLModel, table=True):
    __tablename__ = 'auth_account'
    profile: 'ProfileMod' = Relationship(back_populates='account', sa_relationship_kwargs={'uselist': False})
    options_rel: list['OptionMod'] = Relationship(back_populates='owner')
    addresses: list['AddressMod'] = Relationship(back_populates='account')
    bans: list['BanMod'] = Relationship(
        back_populates='account', sa_relationship_kwargs={'foreign_keys': '[BanMod.recipient_id]'})
    ban_owners: list['BanMod'] = Relationship(
        back_populates='banner', sa_relationship_kwargs={'foreign_keys': '[BanMod.owner_id]'})


    def __repr__(self):
        return f'<Account {self.id}: {self.email}>'  # noqa
