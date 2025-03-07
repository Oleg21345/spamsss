from BaseModel import async_ses
from STelegram import STelegramAdd, STelegram
from sqlalchemy import select, delete
from database import ChackedTelegramList, TelegramList
import datetime

class MetodForSql:
    @classmethod
    async def post_phone(cls, contacts: list[str]) -> None:
        async with async_ses() as session:
            for phone in contacts:
                telegram = TelegramList(number_phone=phone)
                session.add(telegram)
            await session.commit()

    @classmethod
    async def get_phone(cls):
        async with async_ses() as session:
            res = await session.execute(select(TelegramList))
            return res.scalars().all()

    @classmethod
    async def get_checked_phone(cls):
        async with async_ses() as session:
            res = await session.execute(select(ChackedTelegramList))
            return res.scalars().all()

    @classmethod
    async def post_checked_phone(cls, contacts: list[tuple[str, str]]) -> None:
        async with async_ses() as session:
            for phone, sent_at in contacts:
                telegram = ChackedTelegramList(number_phone=phone, sent_at=sent_at)
                session.add(telegram)
            try:
                await session.commit()
                print("✅ Контакти успішно додані")
            except Exception as e:
                print(f"❌ Помилка при коміті: {e}")
                await session.rollback()

    @classmethod
    async def delete_phone(cls, contacts: list[str]) -> None:
        async with async_ses() as session:
            try:
                result = await session.execute(
                    select(TelegramList.number_phone).where(TelegramList.number_phone.in_(contacts))
                )
                found_numbers = [row[0] for row in result.all()]
                await session.execute(
                    delete(TelegramList).where(TelegramList.number_phone.in_(contacts))
                )
                await session.flush()
                await session.commit()
            except Exception as e:
                await session.rollback()

