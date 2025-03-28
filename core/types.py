from typing import Annotated
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import Depends

from .config import get_session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
