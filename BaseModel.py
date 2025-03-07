from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine("sqlite+aiosqlite:///books.db")
async_ses = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

