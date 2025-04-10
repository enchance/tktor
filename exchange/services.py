from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from .Trades import Exchange


class ExchangeSvc:
    @staticmethod
    async def get_exchange(name: str, *, session: AsyncSession):
        stmt = select(Exchange).where(Exchange.name == name)
        exec_ = await session.exec(stmt)
        xch = exec_.one_or_none()
        return xch


    # PLACEHOLDER: To follow
    @staticmethod
    async def get_orders():
        pass


    # PLACEHOLDER: To follow
    @staticmethod
    async def get_trades():
        pass


    # PLACEHOLDER: To follow
    @staticmethod
    async def update_pointer():
        pass
