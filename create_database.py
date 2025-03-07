from sqlalchemy.sql.util import expand_column_list_from_order_by
from BaseModel import engine, Base

async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tabl():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)




