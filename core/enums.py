from __future__ import annotations
from enum import StrEnum, IntEnum, auto
from typing import Literal


LitActiveAll = Literal['ACTIVE', 'INACTIVE', 'ALL']


class Envs(StrEnum):
    development = auto()
    staging = auto()
    production = auto()


    def __eq__(self, other: Envs | str):
        if isinstance(other, Envs):
            return self.name == other.name
        return self.name == other


class CommentStatus(StrEnum):
    cancelled = auto()
    drafted = auto()
    pending = auto()
    published = auto()


class OptionType(IntEnum):
    system = 1
    user = 2
