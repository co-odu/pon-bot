import asyncio
import os
from datetime import datetime
from collections import defaultdict
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_LINK = "https://t.me/co_odu_w"
ADMIN_ID = 6235378997

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== БАЗА ДАННЫХ В ПАМЯТИ ==========
users_db = {}
stats = {
    "total": 0,
    "by_category": defaultdict(int),
    "helped_yes": 0,
    "helped_no": 0,
    "today": defaultdict(int),
    "history": []
}
registration_state = {}
current_address = {}

# ========== КЛАВИАТУРЫ ==========

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🆘 Проблема")],
        [KeyboardButton(text="📋 Мои обращения"), KeyboardButton(text="⭐ Оценить")],
        [KeyboardButton(text="🏪 Мои точки"), KeyboardButton(text="📊 Статистика")]
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

role_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍩 Пон-мастер")],
        [KeyboardButton(text="👔 Управляющий")],
        [KeyboardButton(text="🏢 Собственник")]
    ],
    resize_keyboard=True
)


# ========== ЛОГИРОВАНИЕ ==========

async def log_to_admin(text: str):
    try:
        await bot.send_message(ADMIN_ID, text, parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"Ошибка отправки лога: {e}")


# ========== ХЕЛПЕР: клавиатура точек ==========

def make_address_keyboard(user_id):
    addresses = users_db[user_id].get("addresses", [])
    keyboard = []
    for addr in addresses:
        keyboard.append([KeyboardButton(text=f"📍 {addr}")])
    keyboard.append([KeyboardButton(text="➕ Добавить новую точку")])
    keyboard.append([KeyboardButton(text="⬅️ Назад в главное меню")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


# ========== РЕГИСТРАЦИЯ (3 шага) ==========

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    user = message.from_user
    
    if user_id in users_db:
        await message.answer(
            f"👋 Снова привет, <b>{users_db[user_id]['display_name']}</b>!\n"
            f"👤 Должность: {users_db[user_id]['role']}\n"
            f"🏪 Точек: {len(users_db[user_id].get('addresses', []))}\n\n"
            f"Выбери действие в меню ниже 👇",
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu
        )
        return
    
    registration_state[user_id] = {"step": "waiting_name", "data": {}}
    await message.answer(
        "👋 Привет! Я бот поддержки сети пончиковых <b>PON-PUSHKA</b>.\n\n"
        "Для начала работы нужно пройти быструю регистрацию.\n\n"
        "📝 <b>Шаг 1 из 3</b>\n"
        "Как к тебе обращаться? Введи своё <b>имя</b>:\n\n"
        "Пример: <code>Иван</code> или <code>Иван Петров</code>",
        parse_mode=ParseMode.HTML
    )


@dp.message(lambda msg: msg.from_user.id in registration_state and registration_state[msg.from_user.id]["step"] == "waiting_name")
async def process_name(message: Message):
    user_id = message.from_user.id
    name = message.text.strip()
    
    registration_state[user_id]["data"]["display_name"] = name
    registration_state[user_id]["step"] = "waiting_address"
    
    await message.answer(
        f"✅ Приятно познакомиться, <b>{name}</b>!\n\n"
        f"📝 <b>Шаг 2 из 3</b>\n"
        f"Введи <b>полный адрес</b> точки:\n"
        f"<i>город, улица, номер дома</i>\n\n"
        f"Пример: <code>Минск, пр. Независимости, 15</code>",
        parse_mode=ParseMode.HTML
    )


@dp.message(lambda msg: msg.from_user.id in registration_state and registration_state[msg.from_user.id]["step"] == "waiting_address")
async def process_first_address(message: Message):
    user_id = message.from_user.id
    
    users_db[user_id] = {
        "name": message.from_user.full_name,
        "username": message.from_user.username or "",
        "display_name": registration_state[user_id]["data"]["display_name"],
        "addresses": [message.text.strip()]
    }
    registration_state[user_id]["data"]["address"] = message.text.strip()
    registration_state[user_id]["step"] = "waiting_role"
    
    await message.answer(
        f"✅ Адрес сохранён:\n<b>{message.text.strip()}</b>\n\n"
        f"📝 <b>Шаг 3 из 3</b>\n"
        f"Выбери свою должность:",
        parse_mode=ParseMode.HTML,
        reply_markup=role_menu
    )


@dp.message(lambda msg: msg.from_user.id in registration_state and registration_state[msg.from_user.id]["step"] == "waiting_role")
async def process_role(message: Message):
    user_id = message.from_user.id
    role = message.text.strip()
    role_clean = role.replace("🍩 ", "").replace("👔 ", "").replace("🏢 ", "")
    
    users_db[user_id]["role"] = role_clean
    del registration_state[user_id]
    
    display_name = users_db[user_id]["display_name"]
    address = users_db[user_id]["addresses"][0]
    
    await log_to_admin(
        f"🆕 <b>Новый пользователь зарегистрирован!</b>\n"
        f"👤 Имя: <b>{display_name}</b>\n"
        f"🆔 Telegram: {users_db[user_id]['name']} (@{users_db[user_id]['username'] or 'нет'})\n"
        f"📍 Адрес: {address}\n"
        f"👤 Должность: {role_clean}\n"
        f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
    )
    
    await message.answer(
        f"🎉 <b>Регистрация завершена!</b>\n\n"
        f"👤 Имя: <b>{display_name}</b>\n"
        f"📍 Адрес: {address}\n"
        f"👤 Должность: {role_clean}\n\n"
        f"Если у тебя несколько точек — добавь их через меню <b>🏪 Мои точки</b>.\n\n"
        f"Выбери действие 👇",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu
    )


# ========== ДОБАВЛЕНИЕ НОВОЙ ТОЧКИ ==========

@dp.message(lambda msg: msg.text == "🏪 Мои точки")
async def handle_my_shops(message: Message):
    user_id = message.from_user.id
    
    if user_id not in users_db:
        await message.answer("⚠️ Сначала пройди регистрацию — нажми /start")
        return
    
    addresses = users_db[user_id].get("addresses", [])
    display_name = users_db[user_id].get("display_name", "Пользователь")
    
    text = f"🏪 <b>Точки {display_name}</b> ({len(addresses)}):\n\n"
    for i, addr in enumerate(addresses, 1):
        text += f"{i}. 📍 {addr}\n"
    
    text += "\nНажми <b>➕ Добавить новую точку</b>, чтобы добавить ещё одну."
    
    await message.answer(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=make_address_keyboard(user_id)
    )


@dp.message(lambda msg: msg.text == "➕ Добавить новую точку")
async def handle_add_shop(message: Message):
    user_id = message.from_user.id
    
    if user_id not in users_db:
        await message.answer("⚠️ Сначала пройди регистрацию — нажми /start")
        return
    
    registration_state[user_id] = {"step": "adding_new_address", "data": {}}
    await message.answer(
        "📝 Введи адрес <b>новой точки</b>:\n"
        "<i>город, улица, номер дома</i>\n\n"
        "Пример: <code>Гродно, Советская, 8</code>",
        parse_mode=ParseMode.HTML
    )


@dp.message(lambda msg: msg.from_user.id in registration_state and registration_state[msg.from_user.id]["step"] == "adding_new_address")
async def process_new_address(message: Message):
    user_id = message.from_user.id
    new_address = message.text.strip()
    
    users_db[user_id]["addresses"].append(new_address)
    del registration_state[user_id]
    
    display_name = users_db[user_id].get("display_name", "Пользователь")
    
    await log_to_admin(
        f"🏪 <b>Добавлена новая точка!</b>\n"
        f"👤 Пользователь: <b>{display_name}</b>\n"
        f"📍 Новый адрес: {new_address}\n"
        f"🏪 Всего точек: {len(users_db[user_id]['addresses'])}"
    )
    
    await message.answer(
        f"✅ Точка добавлена:\n<b>{new_address}</b>\n\n"
        f"🏪 Всего точек: {len(users_db[user_id]['addresses'])}\n\n"
        f"Выбери действие 👇",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu
    )


# ========== ВЫБОР ТОЧКИ ПЕРЕД ПРОБЛЕМОЙ ==========

@dp.message(lambda msg: msg.text == "🆘 Проблема")
async def handle_problem(message: Message):
    user_id = message.from_user.id
    
    if user_id not in users_db:
        await message.answer("⚠️ Сначала пройди регистрацию — нажми /start")
        return
    
    addresses = users_db[user_id].get("addresses", [])
    
    if len(addresses) == 1:
        current_address[user_id] = addresses[0]
        await message.answer(
            f"📍 Точка: <b>{addresses[0]}</b>\n\n"
            f"Выбери категорию проблемы 👇",
            reply_markup=problem_menu
        )
    else:
        await message.answer(
            "🏪 Выбери точку, с которой обращение:",
            parse_mode=ParseMode.HTML,
            reply_markup=make_address_keyboard(user_id)
        )


@dp.message(lambda msg: msg.text.startswith("📍 "))
async def handle_select_address(message: Message):
    user_id = message.from_user.id
    selected = message.text.replace("📍 ", "").strip()
    
    if user_id not in users_db:
        await message.answer("⚠️ Сначала пройди регистрацию — нажми /start")
        return
    
    addresses = users_db[user_id].get("addresses", [])
    if selected in addresses:
        current_address[user_id] = selected
        await message.answer(
            f"✅ Выбрана точка:\n<b>{selected}</b>\n\n"
            f"Выбери категорию проблемы 👇",
            parse_mode=ParseMode.HTML,
            reply_markup=problem_menu
        )
    else:
        await message.answer(
            "⚠️ Такой точки нет в списке. Выбери из меню.",
            reply_markup=make_address_keyboard(user_id)
        )


# ========== ОСТАЛЬНЫЕ КНОПКИ ==========

@dp.message(lambda msg: msg.text == "📋 Мои обращения")
async def handle_history(message: Message):
    await message.answer(
        "📋 <b>Функция в разработке</b>\n\n"
        "Спасибо за терпение и тестирование! 🙏",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu
    )


@dp.message(lambda msg: msg.text == "⭐ Оценить")
async def handle_rate(message: Message):
    await message.answer(
        "⭐ <b>Функция в разработке</b>\n\n"
        "Спасибо за терпение и тестирование! 🙏",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu
    )


@dp.message(lambda msg: msg.text == "📊 Статистика")
async def handle_stats_button(message: Message):
    await message.answer(
        "📊 <b>Функция в разработке</b>\n\n"
        "Спасибо за терпение и тестирование! 🙏",
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu
    )


@dp.message(lambda msg: msg.text == "⬅️ Назад в главное меню")
async def handle_back(message: Message):
    user_id = message.from_user.id
    if user_id in current_address:
        del current_address[user_id]
    await message.answer(
        "Главное меню 👇",
        reply_markup=main_menu
    )


# ========== ПРОБЛЕМЫ ==========

@dp.message(lambda msg: msg.text in ["🧾 Чек", "💳 Оплата", "☕ Кофе-машина", "🍩 Аппарат", "🔧 Другое"])
async def handle_problem_category(message: Message):
    user_id = message.from_user.id
    user = message.from_user
    chat = message.chat
    category = message.text
    time_now = datetime.now()
    today_str = time_now.strftime("%d.%m.%Y")
    
    if user_id not in users_db:
        await message.answer("⚠️ Сначала пройди регистрацию — нажми /start")
        return
    
    if user_id not in current_address:
        await message.answer(
            "🏪 Сначала выбери точку через меню <b>🆘 Проблема</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    stats["total"] += 1
    stats["by_category"][category] += 1
    stats["today"][today_str] += 1
    
    user_data = users_db[user_id]
    selected_address = current_address[user_id]
    display_name = user_data.get("display_name", user.full_name)
    
    record = {
        "time": time_now,
        "category": category,
        "user": user.full_name,
        "display_name": display_name,
        "user_id": user_id,
        "address": selected_address,
        "role": user_data["role"],
        "chat": chat.title or "Личка"
    }
    stats["history"].append(record)
    
    await log_to_admin(
        f"🆘 <b>Новое обращение #{stats['total']}</b>\n"
        f"👤 Имя: <b>{display_name}</b>\n"
        f"📍 Адрес: <b>{selected_address}</b>\n"
        f"👤 Должность: <b>{user_data['role']}</b>\n"
        f"🆔 Telegram: {user.full_name} (@{user.username or 'нет'})\n"
        f"📂 Категория: {category}\n"
        f"💬 Чат: {chat.title or 'Личка'} (ID: <code>{chat.id}</code>)\n"
        f"⏰ Время: {time_now.strftime('%H:%M %d.%m.%Y')}"
    )
    
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
        f"📍 Точка: <b>{selected_address}</b>\n\n"
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
    
    stats["helped_yes"] += 1
    
    await log_to_admin(
        f"✅ <b>Помогло!</b> (Всего: {stats['helped_yes']})\n"
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
    
    stats["helped_no"] += 1
    
    await log_to_admin(
        f"❌ <b>НЕ помогло — нужен менеджер!</b> (Всего: {stats['helped_no']})\n"
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


# ========== СТАТИСТИКА ДЛЯ АДМИНА ==========

@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Эта команда только для администратора.")
        return
    
    today = datetime.now().strftime("%d.%m.%Y")
    today_total = stats["today"].get(today, 0)
    
    by_address = defaultdict(int)
    by_role = defaultdict(int)
    for record in stats["history"]:
        by_address[record.get("address", "Неизвестно")] += 1
        by_role[record.get("role", "Неизвестно")] += 1
    
    text = (
        f"📊 <b>Статистика обращений</b>\n\n"
        f"📈 <b>Всего обращений:</b> {stats['total']}\n"
        f"📅 <b>Сегодня ({today}):</b> {today_total}\n"
        f"👥 <b>Зарегистрировано пользователей:</b> {len(users_db)}\n\n"
        f"📂 <b>По категориям:</b>\n"
    )
    
    for cat, count in sorted(stats["by_category"].items(), key=lambda x: -x[1]):
        text += f"  • {cat}: {count}\n"
    
    text += f"\n📍 <b>По адресам:</b>\n"
    for addr, count in sorted(by_address.items(), key=lambda x: -x[1]):
        text += f"  • {addr}: {count}\n"
    
    text += f"\n👤 <b>По должностям:</b>\n"
    for role, count in sorted(by_role.items(), key=lambda x: -x[1]):
        text += f"  • {role}: {count}\n"
    
    text += (
        f"\n✅ <b>Помогло:</b> {stats['helped_yes']}\n"
        f"❌ <b>Не помогло:</b> {stats['helped_no']}\n"
    )
    
    if stats["helped_yes"] + stats["helped_no"] > 0:
        success_rate = stats["helped_yes"] / (stats["helped_yes"] + stats["helped_no"]) * 100
        text += f"\n🎯 <b>Процент решений:</b> {success_rate:.1f}%"
    
    await message.answer(text, parse_mode=ParseMode.HTML)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
