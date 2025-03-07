
import gspread
from google.oauth2.service_account import Credentials
from create_database import drop_tabl, create_table
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InputPhoneContact
from metod_class import MetodForSql
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
json_pyt = "braided-topic-443423-v4-d307f39d9be9.json"
sheet_id = "1PJf12s6J2NZL6Ohq3XjORJ45hc1a4bIdQDlGCtiGN1c"

creds = Credentials.from_service_account_file(json_pyt, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(sheet_id).sheet1

async def fetch_contacts_from_google_sheets():
    contacts = sheet.get_all_values()
    numbers = [row[0] for row in contacts if row]
    return numbers

async def save_contacts_to_db(contacts):
    await MetodForSql.post_phone(contacts)

async def main():
    await drop_tabl()
    await create_table()

    contacts = await fetch_contacts_from_google_sheets()
    await save_contacts_to_db(contacts)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


ACCOUNTS = [
    {"session": "account_1", "api_id": 23149586, "api_hash": "d7172ccacacf01096df5486b0da49bed2"},
    {"session": "account_2", "api_id": 24114585, "api_hash": "ef4fbe4d4bd0abaa6ae5a695ccbfb7a5"},
]

current_index = 0
checked_phones = set()
group_chat_id = -1002389936191
scheduler = AsyncIOScheduler()

def get_active_account():
    return ACCOUNTS[current_index]

account = get_active_account()
app = Client(account["session"], account["api_id"], account["api_hash"])

async def switch_account():
    global current_index, app
    print("⚠️ Аккаунт заблокирован, переключаюсь...")

    current_index += 1
    if current_index >= len(ACCOUNTS):
        print("❌ Все аккаунты заблокированы!")
        return False

    account = get_active_account()
    app = Client(account["session"], account["api_id"], account["api_hash"])
    await app.start()
    return True

async def send_message_batch(message_text, num_contacts):
    print("📋 Получаем номера...")
    phones = await MetodForSql.get_phone()

    if not phones:
        print("⚠️ Нет номеров!")
        return

    contacts = [
        InputPhoneContact(phone=str(p.number_phone).strip(), first_name="User", last_name="")
        for p in phones if str(p.number_phone).strip() not in checked_phones
    ][:num_contacts]

    if not contacts:
        print("⚠️ Все номера обработаны!")
        return

    print(f"📋 Добавляем контакты: {len(contacts)}")

    try:
        added_contact = await app.import_contacts(contacts)
    except Exception as e:
        print(f"❌ Ошибка добавления контактов: {e}")
        if "deleted/deactivated" in str(e) or "flood" in str(e):
            if await switch_account():
                return

    users = added_contact.users or []
    processed_numbers = []

    for user in users:
        phone_str = str(user.phone).strip()
        if phone_str not in checked_phones:
            print(f"✅ Контакт {user.phone} добавлен! ID: {user.id}")
            try:
                await app.send_message(user.id, message_text)
                print(f"✅ Сообщение отправлено {user.id}")
            except Exception as e:
                print(f"❌ Ошибка отправки сообщения {user.id}: {e}")

            checked_phones.add(phone_str)
            processed_numbers.append((phone_str, datetime.datetime.utcnow()))

    if processed_numbers:
        await MetodForSql.post_checked_phone(processed_numbers)
        await MetodForSql.delete_phone([p[0] for p in processed_numbers])

    print("✅ Все сообщения отправлены.")

async def setup_scheduler():
    while True:
        try:
            num_contacts = int(input("Сколько сообщений отправлять в день? (Enter, чтобы оставить прошлое): ") or "2")
            if num_contacts <= 0:
                print("❌ Число должно быть больше нуля!")
                continue
            break
        except ValueError:
            print("❌ Введите корректное число!")

    while True:
        send_time = input("Введите время отправки сообщения (HH:MM) (Enter, чтобы оставить прошлое): ").strip()
        if not send_time:
            send_time = "16:23"
        try:
            hours, minutes = map(int, send_time.split(":"))
            if 0 <= hours < 24 and 0 <= minutes < 60:
                break
        except ValueError:
            print("❌ Неправильное время!")

    message_text = input("Введите текст сообщения (Enter, чтобы оставить прошлое): ").strip() or "gsgs"

    scheduler.add_job(send_message_batch, "cron", hour=hours, minute=minutes, args=[message_text, num_contacts])
    scheduler.start()

    print("✅ Расписание обновлено! Бот будет отправлять сообщения автоматически.")


async def main():
    await setup_scheduler()

    await app.start()
    print("Бот запущен!")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Остановка бота...")
    finally:
        await app.stop()
        print("Бот остановлен.")


@app.on_message(filters.private)
async def forward_to_group(_, message):
    user_id = message.from_user.username or message.from_user.id
    text = message.text or "(не текстовое сообщение)"

    print(f"📩 Сообщение от {user_id}: {text}")

    if not text:
        print("❌ Сообщение пустое.")
        return

    try:
        print("📤 Отправка сообщения в группу...")
        await app.send_message(group_chat_id, f"📨 Новое сообщение от {user_id}:\n{text}")

        await message.reply("""
        Спасибо за сообщение! Давайте продолжим общение в боте! https://t.me/cubecrm_bot
        """)
    except Exception as e:
        print(f"❌ Ошибка отправки в группу: {e}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
































# import gspread
# from google.oauth2.service_account import Credentials
# from create_database import drop_tabl,  create_table
# import asyncio
# from pyrogram import Client, filters
# from pyrogram.types import InputPhoneContact
# from metod_class import MetodForSql
# import datetime
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
#
# SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# json_pyt = "braided-topic-443423-v4-d307f39d9be9.json"
# sheet_id = "1PJf12s6J2NZL6Ohq3XjORJ45hc1a4bIdQDlGCtiGN1c"
#
#
# creds = Credentials.from_service_account_file(json_pyt, scopes=SCOPES)
# client = gspread.authorize(creds)
# sheet = client.open_by_key(sheet_id).sheet1
#
#
# async def fetch_contacts_from_google_sheets():
#     contacts = sheet.get_all_values()
#     numbers = [row[1] for row in contacts if row]
#     return numbers
#
#
# async def save_contacts_to_db(contacts):
#     await MetodForSql.post_phone(contacts)
#
#
# async def main():
#     await drop_tabl()
#     await create_table()
#
#     contacts = await fetch_contacts_from_google_sheets()
#     await save_contacts_to_db(contacts)
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
#
#
#
# ACCOUNTS = [
#     {"session": "account_1", "api_id": 24873004, "api_hash": "0e6be7ea172fe48da7d1f9747f473dd2"},
#     {"session": "account_2", "api_id": 28604332, "api_hash": "0d86c58a3dc3868293c145c041ef131c"},
# ]
#
# current_index = 0
# checked_phones = set()
# group_chat_id = -1002450489802
# scheduler = AsyncIOScheduler()
#
#
# def get_active_account():
#     return ACCOUNTS[current_index]
#
#
# account = get_active_account()
# app = Client(account["session"], account["api_id"], account["api_hash"])
#
#
# async def switch_account():
#     global current_index, app
#     print("⚠️ Аккаунт заблокирован, переключаюсь...")
#
#     current_index += 1
#     if current_index >= len(ACCOUNTS):
#         print("❌ Все аккаунты заблокированы!")
#         return False
#
#     account = get_active_account()
#     app = Client(account["session"], account["api_id"], account["api_hash"])
#     await app.start()
#     return True
#
#
# async def send_message_batch(message_text, num_contacts):
#     print("📋 Получаем номера...")
#     phones = await MetodForSql.get_phone()
#
#     if not phones:
#         print("⚠️ Нет номеров!")
#         return
#
#     contacts = [
#         InputPhoneContact(phone=str(p.number_phone).strip(), first_name="User", last_name="")
#         for p in phones if str(p.number_phone).strip() not in checked_phones
#     ][:num_contacts]
#
#     if not contacts:
#         print("⚠️ Все номера обработаны!")
#         return
#
#     print(f"📋 Добавляем контакты: {len(contacts)}")
#
#     try:
#         added_contact = await app.import_contacts(contacts)
#     except Exception as e:
#         print(f"❌ Ошибка добавления контактов: {e}")
#         if "deleted/deactivated" in str(e) or "flood" in str(e):
#             if await switch_account():
#                 return
#
#     users = added_contact.users or []
#     processed_numbers = []
#
#     for user in users:
#         phone_str = str(user.phone).strip()
#         if phone_str not in checked_phones:
#             print(f"✅ Контакт {user.phone} добавлен! ID: {user.id}")
#             try:
#                 await app.send_message(user.id, message_text)
#                 print(f"✅ Сообщение отправлено {user.id}")
#             except Exception as e:
#                 print(f"❌ Ошибка отправки сообщения {user.id}: {e}")
#
#             checked_phones.add(phone_str)
#             processed_numbers.append((phone_str, datetime.datetime.utcnow()))
#
#     if processed_numbers:
#         await MetodForSql.post_checked_phone(processed_numbers)
#         await MetodForSql.delete_phone([p[0] for p in processed_numbers])
#
#     print("✅ Все сообщения отправлены.")
#
#
#
#
# async def send_messages():
#     while True:
#         try:
#             num_contacts = int(input("Сколько сообщений отправлять в день? (Enter, чтобы оставить прошлое): ") or "2")
#             if num_contacts <= 0:
#                 print("❌ Число должно быть больше нуля!")
#                 continue
#             break
#         except ValueError:
#             print("❌ Введите корректное число!")
#
#     while True:
#         send_time = input("Введите время отправки сообщения (HH:MM) (Enter, чтобы оставить прошлое): ").strip()
#         if not send_time:
#             send_time = "16:23"
#         try:
#             hours, minutes = map(int, send_time.split(":"))
#             if 0 <= hours < 24 and 0 <= minutes < 60:
#                 break
#         except ValueError:
#             print("❌ Неправильное время!")
#
#     message_text = input("Введите текст сообщения (Enter, чтобы оставить прошлое): ").strip() or "gsgs"
#
#     scheduler.add_job(send_message_batch, "cron", hour=hours, minute=minutes, args=[message_text, num_contacts])
#     scheduler.start()
#
#     print("✅ Расписание обновлено! Бот будет отправлять сообщения автоматически.")
#
#     while True:
#         await asyncio.sleep(3600)
#
#
# @app.on_message(filters.private)
# async def forward_to_group(_, message):
#     user_id = message.from_user.username or message.from_user.id
#     text = message.text or "(не текстовое сообщение)"
#
#     print(f"📩 Сообщение от {user_id}: {text}")
#
#     if not text:
#         print("❌ Сообщение пустое.")
#         return
#
#     try:
#         print("📤 Отправка сообщения в группу...")
#         await app.send_message(group_chat_id, f"📨 Новое сообщение от {user_id}:\n{text}")
#
#         await message.reply("""
#         Спасибо за сообщение! Давайте продолжим общение в боте!
#         https://t.me/cubecrm_bot
#         """)
#     except Exception as e:
#         print(f"❌ Ошибка отправки в группу: {e}")
#
#
#
# async def main():
#     async with app:
#         asyncio.create_task(send_messages())
#         await send_messages()
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
#
#
