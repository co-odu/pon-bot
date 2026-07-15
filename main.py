import asyncio
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_LINK = "https://t.me/co_odu_w"
ADMIN_ID = 6235378997  # ← ЗАМЕНИ на свой ID от @userinfobot

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


# ========== ЛОГИРОВАНИЕ ==========

async def log_to_admin(text: str):
    """Отправляет лог админу в личку"""
    try:
        await bot.send_message(ADMIN_ID, text, parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"Ошибка отправки лога: {e}")


# ========== ОБРАБОТЧИКИ ==========

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    chat = message.chat
    
    # Логируем /start
    await log_to_admin(
        f"🚀 <b>Новый запуск бота</b>\n"
        f"👤 Пользователь: {user.full_name} (@{user.username or 'нет'})\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"💬 Чат: {chat.title or 'Личка'} (ID: <code>{chat.id}</code>)\n"
        f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
    )
    
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


# ========== ПРОБЛЕМЫ С ЛОГИРОВАНИЕМ ==========

@dp.message(lambda msg: msg.text in ["🧾 Чек", "💳 Оплата", "☕ Кофе-машина", "🍩 Аппарат", "🔧 Другое"])
async def handle_problem_category(message: Message):
    user = message.from_user
    chat = message.chat
    category = message.text
    time_now = datetime.now().strftime('%H:%M %d.%m.%Y')
    
    # Логируем обращение
    await log_to_admin(
        f"🆘 <b>Новое обращение</b>\n"
        f"📂 Категория: {category}\n"
        f"👤 От: {user.full_name} (@{user.username or 'нет'})\n"
        f"💬 Чат: {chat.title or 'Личка'} (ID: <code>{chat.id}</code>)\n"
        f"⏰ Время: {time_now}"
    )
    
    # Ответ пользователю
    guides = {
        "🧾 Чек": ("🧾 Проблема с чеком", [
            "Проверьте бумагу в принтере",
            "Перезагрузите терминал",
            "Проверьте интернет"
        ]),
        "💳 Оплата": ("💳 Проблема с оплатой", [
            "Проверьте интернет",
            "Перезагрузите терминал",
            "Попробуйте другую карту"
        ]),
        "☕ Кофе-машина": ("☕ Проблема с кофе-машиной", [
            "Проверьте уровень воды",
            "Очистите поддон",
            "Проверьте зёрна"
        ]),
        "🍩 Аппарат": ("🍩 Проблема с аппаратом", [
            "Проверьте уровень масла",
            "Проверьте температуру",
            "Очистите фильтр"
        ]),
        "🔧 Другое": ("🔧 Другая проблема", [
            "Опишите проблему подробнее",
            "Сделайте фото ошибки",
            "Свяжитесь с менеджером"
        ])
    }
    
    title, steps = guides[category]
    steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
    
    await message.answer(
        f"{title}\n\n"
        f"🚧 <b>Функция в разработке</b>\n\n"
        f"Спасибо за терпение и тестирование! 🙏\n"
        f"Скоро здесь появится подробный гайд.\n\n"
        f"Пока что попробуйте:\n{steps_text}",
        parse_mode=ParseMode.HTML,
        reply_markup=helpful_inline
    )


# ========== INLINE КНОПКИ ==========

@dp.callback_query(F.data == "helped_yes")
async def callback_helped_yes(callback):
    user = callback.from_user
    chat = callback.message.chat
    
    # Логируем оценку
    await log_to_admin(
        f"✅ <b>Помогло!</b>\n"
        f"👤 Пользователь: {user.full_name}\n"
        f"💬 Чат: {chat.title or 'Личка'}\n"
        f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
    )
    
    await callback.message.edit_text(
        callback.message.text + "\n\n✅ <b>Рад помочь!</b> Если что-то ещё понадобится — обращайтесь.",
        parse_mode=ParseMode.HTML
    )
    await callback.answer("Спасибо за обратную связь!")


@dp.callback_query(F.data == "helped_no")
async def callback_helped_no(callback):
    user = callback.from_user
    chat = callback.message.chat
    
    # Логируем эскалацию
    await log_to_admin(
        f"❌ <b>НЕ помогло — нужен менеджер!</b>\n"
        f"👤 Пользователь: {user.full_name}\n"
        f"💬 Чат: {chat.title or 'Личка'}\n"
        f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}\n"
        f"🔗 Ссылка: {MANAGER_LINK}"
    )
    
    await callback.message.edit_text(
        callback.message.text + f"\n\n❌ <b>Свяжитесь с менеджером:</b>\n{MANAGER_LINK}",
        parse_mode=ParseMode.HTML
    )
    await callback.answer("Передаём менеджеру!")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
