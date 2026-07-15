import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_LINK = "https://t.me/co_odu_w"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== КЛАВИАТУРЫ ==========

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🆘 Проблема")],
        [KeyboardButton(text="📋 Мои обращения"), KeyboardButton(text="⭐ Оценить")],
        [KeyboardButton(text="📊 Статистика")]
    ],
    resize_keyboard=True
)

problem_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧾 Чек"), KeyboardButton(text="💳 Оплата")],
        [KeyboardButton(text="☕ Кофе-машина"), KeyboardButton(text="🍩 Аппарат")],
        [KeyboardButton(text="🔧 Другое")],
        [KeyboardButton(text="⬅️ Назад в главное меню")]
    ],
    resize_keyboard=True
)

helpful_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Помогло", callback_data="helped_yes"),
            InlineKeyboardButton(text="❌ Не помогло", callback_data="helped_no")
        ]
    ]
)


# ========== ОБРАБОТЧИКИ ==========

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я бот поддержки сети пончиковых <b>PON-PUSHKA</b>.\n\n"
        "Выбери действие в меню ниже 👇",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu
    )


@dp.message(lambda msg: msg.text == "🆘 Проблема")
async def handle_problem(message: Message):
    await message.answer(
        "Выбери категорию проблемы 👇",
        reply_markup=problem_menu
    )


@dp.message(lambda msg: msg.text == "📋 Мои обращения")
async def handle_history(message: Message):
    await message.answer(
        "📋 <b>Функция в разработке</b>\n\n"
        "Спасибо за терпение и тестирование! 🙏\n"
        "Скоро здесь появится история ваших обращений.",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu
    )


@dp.message(lambda msg: msg.text == "⭐ Оценить")
async def handle_rate(message: Message):
    await message.answer(
        "⭐ <b>Функция в разработке</b>\n\n"
        "Спасибо за терпение и тестирование! 🙏\n"
        "Скоро здесь можно будет оценить работу поддержки.",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu
    )


@dp.message(lambda msg: msg.text == "📊 Статистика")
async def handle_stats(message: Message):
    await message.answer(
        "📊 <b>Функция в разработке</b>\n\n"
        "Спасибо за терпение и тестирование! 🙏\n"
        "Скоро здесь появится статистика по проблемам.",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu
    )


@dp.message(lambda msg: msg.text == "⬅️ Назад в главное меню")
async def handle_back(message: Message):
    await message.answer(
        "Главное меню 👇",
        reply_markup=main_menu
    )


@dp.message(lambda msg: msg.text == "🧾 Чек")
async def handle_check(message: Message):
    await message.answer(
        "🧾 <b>Проблема с чеком</b>\n\n"
        "🚧 <b>Функция в разработке</b>\n\n"
        "Спасибо за терпение и тестирование! 🙏\n"
        "Скоро здесь появится подробный гайд по решению проблемы.\n\n"
        "Пока что попробуйте:\n"
        "1. Проверьте бумагу в принтере\n"
        "2. Перезагрузите терминал\n"
        "3. Проверьте интернет",
        parse_mode=ParseMode.HTML,
        reply_markup=helpful_inline
    )


@dp.message(lambda msg: msg.text == "💳 Оплата")
async def handle_payment(message: Message):
    await message.answer(
        "💳 <b>Проблема с оплатой</b>\n\n"
        "🚧 <b>Функция в разработке</b>\n\n"
        "Спасибо за терпение и тестирование! 🙏\n"
        "Скоро здесь появится подробный гайд по решению проблемы.\n\n"
        "Пока что попробуйте:\n"
        "1. Проверьте интернет\n"
        "2. Перезагрузите терминал\n"
        "3. Попробуйте другую карту",
        parse_mode=ParseMode.HTML,
        reply_markup=helpful_inline
    )


@dp.message(lambda msg: msg.text == "☕ Кофе-машина")
async def handle_coffee(message: Message):
    await message.answer(
        "☕ <b>Проблема с кофе-машиной</b>\n\n"
        "🚧 <b>Функция в разработке</b>\n\n"
        "Спасибо за терпение и тестирование! 🙏\n"
        "Скоро здесь появится подробный гайд по решению проблемы.\n\n"
        "Пока что попробуйте:\n"
        "1. Проверьте уровень воды\n"
        "2. Очистите поддон\n"
        "3. Проверьте зёрна",
        parse_mode=ParseMode.HTML,
        reply_markup=helpful_inline
    )


@dp.message(lambda msg: msg.text == "🍩 Аппарат")
async def handle_fryer(message: Message):
    await message.answer(
        "🍩 <b>Проблема с аппаратом</b>\n\n"
        "🚧 <b>Функция в разработке</b>\n\n"
        "Спасибо за терпение и тестирование! 🙏\n"
        "Скоро здесь появится подробный гайд по решению проблемы.\n\n"
        "Пока что попробуйте:\n"
        "1. Проверьте уровень масла\n"
        "2. Проверьте температуру\n"
        "3. Очистите фильтр",
        parse_mode=ParseMode.HTML,
        reply_markup=helpful_inline
    )


@dp.message(lambda msg: msg.text == "🔧 Другое")
async def handle_other(message: Message):
    await message.answer(
        "🔧 <b>Другая проблема</b>\n\n"
        "🚧 <b>Функция в разработке</b>\n\n"
        "Спасибо за терпение и тестирование! 🙏\n"
        "Скоро здесь появится возможность описать проблему своими словами.\n\n"
        "Пока что обратитесь к менеджеру 👇",
        parse_mode=ParseMode.HTML,
        reply_markup=helpful_inline
    )


@dp.callback_query(F.data == "helped_yes")
async def callback_helped_yes(callback):
    await callback.message.edit_text(
        callback.message.text + "\n\n✅ <b>Рад помочь!</b> Если что-то ещё понадобится — обращайтесь.",
        parse_mode=ParseMode.HTML
    )
    await callback.answer("Спасибо за обратную связь!")


@dp.callback_query(F.data == "helped_no")
async def callback_helped_no(callback):
    await callback.message.edit_text(
        callback.message.text + f"\n\n❌ <b>Свяжитесь с менеджером:</b>\n{MANAGER_LINK}",
        parse_mode=ParseMode.HTML
    )
    await callback.answer("Передаём менеджеру!")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
