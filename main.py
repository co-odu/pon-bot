import asyncio
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

from database import (
    init_db, save_user, get_user, get_all_users,
    save_request, save_feedback, get_stats, get_all_user_ids,
    get_all_feedbacks
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_LINK = "https://t.me/co_odu_w"
ADMIN_ID = 6235378997

init_db()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

registration_state = {}
current_address = {}
feedback_state = {}
broadcast_state = {}

# ========== КЛАВИАТУРЫ ==========

def get_main_menu(user_id):
    if user_id == ADMIN_ID:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🆘 Проблема")],
                [KeyboardButton(text="💡 Идея / Баг"), KeyboardButton(text="🏪 Мои точки")],
                [KeyboardButton(text="📋 Мои обращения"), KeyboardButton(text="⭐ Оценить")],
                [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="💡 Фидбеки")],
                [KeyboardButton(text="📢 Рассылка")]
            ],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🆘 Проблема")],
                [KeyboardButton(text="💡 Идея / Баг"), KeyboardButton(text="🏪 Мои точки")],
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

role_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍩 Пон-мастер")],
        [KeyboardButton(text="👔 Управляющий")],
        [KeyboardButton(text="🏢 Собственник")]
    ],
    resize_keyboard=True
)

feedback_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💡 Новая идея")],
        [KeyboardButton(text="🐞 Нашёл баг")],
        [KeyboardButton(text="⬅️ Назад в главное меню")]
    ],
    resize_keyboard=True
)


# ========== ХЕЛПЕРЫ ==========

async def log_to_admin(text: str):
    try:
        await bot.send_message(ADMIN_ID, text, parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"Ошибка отправки лога: {e}")


def make_address_keyboard(user_id):
    user = get_user(user_id)
    if not user:
        return get_main_menu(user_id)
    addresses = user.get("addresses", [])
    keyboard = []
    for addr in addresses:
        keyboard.append([KeyboardButton(text=f"📍 {addr}")])
    keyboard.append([KeyboardButton(text="➕ Добавить новую точку")])
    keyboard.append([KeyboardButton(text="⬅️ Назад в главное меню")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


# ========== РЕГИСТРАЦИЯ ==========

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    user = message.from_user
    
    db_user = get_user(user_id)
    if db_user:
        await message.answer(
            f"👋 Снова привет, <b>{db_user['display_name']}</b>!\n"
            f"👤 Должность: {db_user['role']}\n"
            f"🏪 Точек: {len(db_user.get('addresses', []))}\n\n"
            f"Выбери действие в меню ниже 👇",
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_menu(user_id)
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
    user = message.from_user
    role = message.text.strip()
    role_clean = role.replace("🍩 ", "").replace("👔 ", "").replace("🏢 ", "")
    
    data = registration_state[user_id]["data"]
    display_name = data["display_name"]
    address = data["address"]
    
    save_user(
        user_id=user_id,
        name=user.full_name,
        username=user.username or "",
        display_name=display_name,
        role=role_clean,
        addresses=[address]
    )
    
    del registration_state[user_id]
    
    await log_to_admin(
        f"🆕 <b>Новый пользователь зарегистрирован!</b>\n"
        f"👤 Имя: <b>{display_name}</b>\n"
        f"🆔 Telegram: {user.full_name} (@{user.username or 'нет'})\n"
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
        reply_markup=get_main_menu(user_id)
    )


# ========== ТОЧКИ ==========

@dp.message(lambda msg: msg.text == "🏪 Мои точки")
async def handle_my_shops(message: Message):
    user_id = message.from_user.id
    db_user = get_user(user_id)
    
    if not db_user:
        await message.answer("⚠️ Сначала пройди регистрацию — нажми /start")
        return
    
    addresses = db_user.get("addresses", [])
    display_name = db_user.get("display_name", "Пользователь")
    
    text = f"🏪 <b>Точки {display_name}</b> ({len(addresses)}):\n\n"
    for i, addr in enumerate(addresses, 1):
        text += f"{i}. 📍 {addr}\n"
    
    text += "\nНажми <b>➕ Добавить новую точку</b>."
    
    await message.answer(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=make_address_keyboard(user_id)
    )


@dp.message(lambda msg: msg.text == "➕ Добавить новую точку")
async def handle_add_shop(message: Message):
    user_id = message.from_user.id
    
    if not get_user(user_id):
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
    
    db_user = get_user(user_id)
    addresses = db_user.get("addresses", [])
    addresses.append(new_address)
    
    save_user(
        user_id=user_id,
        name=db_user["name"],
        username=db_user["username"],
        display_name=db_user["display_name"],
        role=db_user["role"],
        addresses=addresses
    )
    
    del registration_state[user_id]
    
    await log_to_admin(
        f"🏪 <b>Добавлена новая точка!</b>\n"
        f"👤 Пользователь: <b>{db_user['display_name']}</b>\n"
        f"📍 Новый адрес: {new_address}\n"
        f"🏪 Всего точек: {len(addresses)}"
    )
    
    await message.answer(
        f"✅ Точка добавлена:\n<b>{new_address}</b>\n\n"
        f"🏪 Всего точек: {len(addresses)}\n\n"
        f"Выбери действие 👇",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu(user_id)
    )


# ========== ПРОБЛЕМЫ ==========

@dp.message(lambda msg: msg.text == "🆘 Проблема")
async def handle_problem(message: Message):
    user_id = message.from_user.id
    db_user = get_user(user_id)
    
    if not db_user:
        await message.answer("⚠️ Сначала пройди регистрацию — нажми /start")
        return
    
    addresses = db_user.get("addresses", [])
    
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
    
    db_user = get_user(user_id)
    if not db_user:
        await message.answer("⚠️ Сначала пройди регистрацию — нажми /start")
        return
    
    addresses = db_user.get("addresses", [])
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
            "⚠️ Такой точки нет в списке.",
            reply_markup=make_address_keyboard(user_id)
        )


# ========== ФИДБЕК ==========

@dp.message(lambda msg: msg.text == "💡 Идея / Баг")
async def handle_feedback_menu(message: Message):
    user_id = message.from_user.id
    
    if not get_user(user_id):
        await message.answer("⚠️ Сначала пройди регистрацию — нажми /start")
        return
    
    await message.answer(
        "💡 <b>Обратная связь</b>\n\n"
        "Выбери тип сообщения:\n"
        "• <b>Новая идея</b> — предложение по улучшению\n"
        "• <b>Нашёл баг</b> — что-то работает не так\n\n"
        "Или просто напиши текст — я передам админам.",
        parse_mode=ParseMode.HTML,
        reply_markup=feedback_menu
    )


@dp.message(lambda msg: msg.text in ["💡 Новая идея", "🐞 Нашёл баг"])
async def handle_feedback_type(message: Message):
    user_id = message.from_user.id
    feedback_type = "💡 Идея" if "идея" in message.text else "🐞 Баг"
    
    feedback_state[user_id] = {"type": feedback_type, "waiting": True}
    
    await message.answer(
        f"{feedback_type}\n\n"
        f"Опиши подробно. Что хочешь предложить / что сломалось?\n"
        f"Можешь приложить фото или скриншот.",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⬅️ Отмена")]],
            resize_keyboard=True
        )
    )


@dp.message(lambda msg: msg.from_user.id in feedback_state and feedback_state[msg.from_user.id].get("waiting"))
async def process_feedback(message: Message):
    user_id = message.from_user.id
    db_user = get_user(user_id)
    
    if not db_user:
        await message.answer("⚠️ Ошибка. Нажми /start")
        return
    
    feedback_type = feedback_state[user_id]["type"]
    text = message.text
    
    if text == "⬅️ Отмена":
        del feedback_state[user_id]
        await message.answer("Отменено.", reply_markup=get_main_menu(user_id))
        return
    
    save_feedback(
        user_id=user_id,
        display_name=db_user["display_name"],
        address=db_user["addresses"][0] if db_user["addresses"] else "Неизвестно",
        role=db_user["role"],
        text=f"[{feedback_type}] {text}"
    )
    
    # ВИЗУАЛЬНОЕ ВЫДЕЛЕНИЕ ФИДБЕКА
    await log_to_admin(
        f"🚨🚨🚨 <b>НОВЫЙ ФИДБЕК ОТ ПОЛЬЗОВАТЕЛЯ!</b> 🚨🚨🚨\n\n"
        f"{'━'*25}\n"
        f"👤 Имя: <b>{db_user['display_name']}</b>\n"
        f"📍 Точка: {db_user['addresses'][0] if db_user['addresses'] else 'Неизвестно'}\n"
        f"👤 Должность: {db_user['role']}\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"{'━'*25}\n\n"
        f"📝 <b>Текст:</b>\n<i>{text}</i>\n\n"
        f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
    )
    
    await log_to_admin(
        f"⚠️ <b>ВНИМАНИЕ! ПРОВЕРЬ ФИДБЕК ВЫШЕ!</b> ⚠️\n\n"
        f"👆 Это <b>обратная связь</b>, а не обычное обращение с проблемой.\n"
        f"💡 Пользователь предлагает идею или сообщает о баге.\n"
        f"🔔 <b>Рекомендуется ответить!</b>"
    )
    
    del feedback_state[user_id]
    
    await message.answer(
        "✅ <b>Спасибо!</b> Твоё сообщение отправлено администратору.\n"
        "Если нужно — свяжемся с тобой дополнительно.",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu(user_id)
    )


# ========== РАССЫЛКА ==========

@dp.message(lambda msg: msg.text == "📢 Рассылка")
async def handle_broadcast_button(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Только для администратора.")
        return
    
    broadcast_state[message.from_user.id] = True
    await message.answer(
        "📢 <b>Рассылка</b>\n\n"
        "Введи текст сообщения, которое отправится ВСЕМ зарегистрированным пользователям:\n\n"
        "Пример: <code>Завтра обновление! Добавили гайды по Wi-Fi.</code>\n\n"
        "Для отмены нажми ⬅️ Назад",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⬅️ Назад")]],
            resize_keyboard=True
        )
    )


@dp.message(lambda msg: msg.from_user.id in broadcast_state and broadcast_state[msg.from_user.id])
async def process_broadcast(message: Message):
    user_id = message.from_user.id
    text = message.text
    
    if text == "⬅️ Назад":
        del broadcast_state[user_id]
        await message.answer("Рассылка отменена.", reply_markup=get_main_menu(user_id))
        return
    
    all_users = get_all_user_ids()
    sent = 0
    failed = 0
    
    await message.answer(f"📢 Начинаю рассылку {len(all_users)} пользователям...")
    
    for uid in all_users:
        try:
            await bot.send_message(
                uid,
                f"📢 <b>Сообщение от администрации PON-PUSHKA:</b>\n\n"
                f"{text}\n\n"
                f"⏰ {datetime.now().strftime('%H:%M %d.%m.%Y')}",
                parse_mode=ParseMode.HTML
            )
            sent += 1
        except Exception as e:
            failed += 1
            print(f"Ошибка отправки {uid}: {e}")
    
    del broadcast_state[user_id]
    
    await message.answer(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"📬 Отправлено: {sent}\n"
        f"❌ Ошибок: {failed}\n"
        f"👥 Всего: {len(all_users)}",
        reply_markup=get_main_menu(user_id)
    )


# ========== ОСТАЛЬНЫЕ КНОПКИ ==========

@dp.message(lambda msg: msg.text == "📋 Мои обращения")
async def handle_history(message: Message):
    await message.answer(
        "📋 <b>Функция в разработке</b>\n\n"
        "Спасибо за терпение и тестирование! 🙏",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu(message.from_user.id)
    )


@dp.message(lambda msg: msg.text == "⭐ Оценить")
async def handle_rate(message: Message):
    await message.answer(
        "⭐ <b>Функция в разработке</b>\n\n"
        "Спасибо за терпение и тестирование! 🙏",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu(message.from_user.id)
    )


@dp.message(lambda msg: msg.text == "📊 Статистика")
async def handle_stats_button(message: Message):
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        stats_data = get_stats()
        today = datetime.now().strftime("%d.%m.%Y")
        
        text = (
            f"📊 <b>Статистика обращений</b>\n\n"
            f"📈 <b>Всего обращений:</b> {stats_data['total']}\n"
            f"📅 <b>Сегодня ({today}):</b> {stats_data['today']}\n"
            f"👥 <b>Зарегистрировано:</b> {len(get_all_users())}\n\n"
            f"📂 <b>По категориям:</b>\n"
        )
        
        for cat, count in sorted(stats_data["by_category"].items(), key=lambda x: -x[1]):
            text += f"  • {cat}: {count}\n"
        
        text += f"\n📍 <b>По адресам:</b>\n"
        for addr, count in sorted(stats_data["by_address"].items(), key=lambda x: -x[1]):
            text += f"  • {addr}: {count}\n"
        
        text += f"\n👤 <b>По должностям:</b>\n"
        for role, count in sorted(stats_data["by_role"].items(), key=lambda x: -x[1]):
            text += f"  • {role}: {count}\n"
        
        text += (
            f"\n✅ <b>Помогло:</b> {stats_data['helped_yes']}\n"
            f"❌ <b>Не помогло:</b> {stats_data['helped_no']}\n"
        )
        
        if stats_data["helped_yes"] + stats_data["helped_no"] > 0:
            success_rate = stats_data["helped_yes"] / (stats_data["helped_yes"] + stats_data["helped_no"]) * 100
            text += f"\n🎯 <b>Процент решений:</b> {success_rate:.1f}%"
        
        await message.answer(text, parse_mode=ParseMode.HTML)
        return
    
    await message.answer(
        "📊 <b>Функция в разработке</b>\n\n"
        "Спасибо за терпение и тестирование! 🙏",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu(user_id)
    )


@dp.message(lambda msg: msg.text == "💡 Фидбеки")
async def handle_feedbacks_button(message: Message):
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        await message.answer("⛔ Только для администратора.")
        return
    
    feedbacks = get_all_feedbacks()
    
    if not feedbacks:
        await message.answer(
            "📭 <b>Фидбеков пока нет.</b>\n\n"
            "Пользователи ещё не отправляли идей и багов.",
            parse_mode=ParseMode.HTML
        )
        return
    
    text = f"💡 <b>Все фидбеки</b> ({len(feedbacks)}):\n\n"
    
    for i, fb in enumerate(feedbacks[-10:], 1):
        text += (
            f"{'━'*20}\n"
            f"<b>#{i}</b> | {fb['created_at']}\n"
            f"👤 {fb['display_name']} ({fb['role']})\n"
            f"📍 {fb['address']}\n"
            f"📝 {fb['text'][:100]}{'...' if len(fb['text']) > 100 else ''}\n\n"
        )
    
    await message.answer(text, parse_mode=ParseMode.HTML)


@dp.message(lambda msg: msg.text == "⬅️ Назад в главное меню")
async def handle_back(message: Message):
    user_id = message.from_user.id
    
    if user_id in current_address:
        del current_address[user_id]
    if user_id in feedback_state:
        del feedback_state[user_id]
    if user_id in broadcast_state:
        del broadcast_state[user_id]
    
    await message.answer(
        "Главное меню 👇",
        reply_markup=get_main_menu(user_id)
    )


# ========== ОБРАБОТКА ПРОБЛЕМ ==========

@dp.message(lambda msg: msg.text in ["🧾 Чек", "💳 Оплата", "☕ Кофе-машина", "🍩 Аппарат", "🔧 Другое"])
async def handle_problem_category(message: Message):
    user_id = message.from_user.id
    user = message.from_user
    chat = message.chat
    category = message.text
    
    db_user = get_user(user_id)
    if not db_user:
        await message.answer("⚠️ Сначала пройди регистрацию — нажми /start")
        return
    
    if user_id not in current_address:
        await message.answer(
            "🏪 Сначала выбери точку через меню <b>🆘 Проблема</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    selected_address = current_address[user_id]
    display_name = db_user.get("display_name", user.full_name)
    
    save_request(
        user_id=user_id,
        display_name=display_name,
        address=selected_address,
        role=db_user["role"],
        category=category
    )
    
    await log_to_admin(
        f"🆘 <b>Новое обращение!</b>\n"
        f"👤 Имя: <b>{display_name}</b>\n"
        f"📍 Адрес: <b>{selected_address}</b>\n"
        f"👤 Должность: <b>{db_user['role']}</b>\n"
        f"🆔 Telegram: {user.full_name} (@{user.username or 'нет'})\n"
        f"📂 Категория: {category}\n"
        f"💬 Чат: {chat.title or 'Личка'} (ID: <code>{chat.id}</code>)\n"
        f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
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


# ========== КОМАНДЫ АДМИНА ==========

@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Эта команда только для администратора.")
        return
    
    stats_data = get_stats()
    today = datetime.now().strftime("%d.%m.%Y")
    
    text = (
        f"📊 <b>Статистика обращений</b>\n\n"
        f"📈 <b>Всего обращений:</b> {stats_data['total']}\n"
        f"📅 <b>Сегодня ({today}):</b> {stats_data['today']}\n"
        f"👥 <b>Зарегистрировано:</b> {len(get_all_users())}\n\n"
        f"📂 <b>По категориям:</b>\n"
    )
    
    for cat, count in sorted(stats_data["by_category"].items(), key=lambda x: -x[1]):
        text += f"  • {cat}: {count}\n"
    
    text += f"\n📍 <b>По адресам:</b>\n"
    for addr, count in sorted(stats_data["by_address"].items(), key=lambda x: -x[1]):
        text += f"  • {addr}: {count}\n"
    
    text += f"\n👤 <b>По должностям:</b>\n"
    for role, count in sorted(stats_data["by_role"].items(), key=lambda x: -x[1]):
        text += f"  • {role}: {count}\n"
    
    text += (
        f"\n✅ <b>Помогло:</b> {stats_data['helped_yes']}\n"
        f"❌ <b>Не помогло:</b> {stats_data['helped_no']}\n"
    )
    
    if stats_data["helped_yes"] + stats_data["helped_no"] > 0:
        success_rate = stats_data["helped_yes"] / (stats_data["helped_yes"] + stats_data["helped_no"]) * 100
        text += f"\n🎯 <b>Процент решений:</b> {success_rate:.1f}%"
    
    await message.answer(text, parse_mode=ParseMode.HTML)


@dp.message(Command("feedbacks"))
async def cmd_feedbacks(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Только для администратора.")
        return
    
    feedbacks = get_all_feedbacks()
    
    if not feedbacks:
        await message.answer(
            "📭 <b>Фидбеков пока нет.</b>\n\n"
            "Пользователи ещё не отправляли идей и багов.",
            parse_mode=ParseMode.HTML
        )
        return
    
    text = f"💡 <b>Все фидбеки</b> ({len(feedbacks)}):\n\n"
    
    for i, fb in enumerate(feedbacks[-10:], 1):
        text += (
            f"{'━'*20}\n"
            f"<b>#{i}</b> | {fb['created_at']}\n"
            f"👤 {fb['display_name']} ({fb['role']})\n"
            f"📍 {fb['address']}\n"
            f"📝 {fb['text'][:100]}{'...' if len(fb['text']) > 100 else ''}\n\n"
        )
    
    await message.answer(text, parse_mode=ParseMode.HTML)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
