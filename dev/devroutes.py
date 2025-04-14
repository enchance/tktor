from fastapi import APIRouter

from core import SessionDep
from .seeder import devrouter


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
    pass
