import os
from contextlib import asynccontextmanager
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv

load_dotenv()


async_engine = create_async_engine(os.getenv('POSTGRES_URL'), echo=False, future=True)
# async_engine_script = create_async_engine(os.getenv('SCRIPT_POSTGRES_URL'), echo=False, future=True)  # script use


async def get_session() -> AsyncSession:
    """
    Return the async session for use in endpoints.
    Refer to: https://chatgpt.com/c/675b9fb2-ec10-8000-a269-35fdbf5d20ef
    """
    async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@asynccontextmanager
async def get_session_context() -> AsyncSession:
    """
    Similar to `get_session` but for app use.
    """
    async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


# @asynccontextmanager
# async def get_session_context_script() -> AsyncSession:
#     """
#     Similar to `get_session` but for script use during development.
#     """
#     async_session = async_sessionmaker(async_engine_script, class_=AsyncSession, expire_on_commit=False)
#     async with async_session() as session:
#         yield session
