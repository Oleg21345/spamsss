import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command

TOKEN = "7944587450:AAFv7yu-gVOWo-oJNWWjqo-O7JOP-cz3Nbw"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_group_id(message: Message):
    if message.chat.type == "supergroup" or message.chat.type == "group":
        chat_id = message.chat.id
        await message.reply(f"Group ID: {chat_id}")
    else:
        await message.reply("This command should be used in a group.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
