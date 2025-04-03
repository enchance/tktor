from sqlmodel import update, select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.common_models import Option


class OptionsSvc:

    @classmethod
    async def update(cls, id_: int, to_save: dict, *, session: AsyncSession) -> list[str]:
        """
        Update user options based on their ID.
        :param id_:         Account id
        :param to_save:     Data to update
        :param session:     AsyncSession
        :return:            List of updated options
        """
        stmt = select(Option).where(Option.account_id == id_, Option.name.in_(to_save.keys()))  # noqa
        exec_ = await session.exec(stmt)  # noqa
        rows = exec_.all()

        ll = []
        for option in rows:
            for key in to_save.keys():
                if option.name == key:
                    if option.value == to_save[key]:
                        break
                    option.value = str(to_save[key])
                    session.add(option)
                    ll.append(key)
                    break
        if ll:
            await session.commit()
        return ll
