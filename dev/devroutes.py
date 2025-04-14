from typing import Literal, LiteralString, reveal_type, TypedDict, Union
from fastapi import APIRouter
from enum import StrEnum, auto

from core import SessionDep
from .seeder import devrouter  # noqa


class EFoo(StrEnum):
    aaa = auto()
    bbb = auto()
    ccc = auto()


LitFoo = Literal['aaa', 'bbb']


# LitFoo = Literal[EFoo.aaa, EFoo.bbb]


def func(x: LitFoo, y: LiteralString):
    pass


i = 1
func('aaa', f'bar1')


@devrouter.get('/')
async def foo(session: SessionDep):
    # item = Item(foo=Foo.BAR, fooint=FooInt.BAR)
    # session.add(item)
    # await session.commit()
    # await session.refresh(item)
    # ic(item)

    # exec_ = await session.exec(select(Item).where(Item.foo == 'bar'))
    # # exec_ = await session.exec(select(Item).where(Item.foo == 1))
    # item = exec_.one_or_none()
    # # ic(type(item), item)
    # ic(type(item.foo), item.foo)

    # account = await Account.get('enchance@gmail.com', session=session)
    # ic(account.options)
    # stmt = select(Account)
    # exec_ = await session.exec(stmt)
    # accounts = exec_.all()
    # for i in accounts:
    #     ic(i.model_dump())
    return True
