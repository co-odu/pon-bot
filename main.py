import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Привет! Я бот поддержки сети пончиковых PON-PUSHKA.\n\nДобавь меня в чат с партнёрами — и я буду автоматически подсказывать решения проблем с оборудованием.\n\nПросто опиши проблему словами, например: «не пробивается чек» или «кофе-машина течёт».")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
