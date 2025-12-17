import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

# === Логирование ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

# === Состояния ===
(
    CHOOSING_CATEGORY,
    CHOOSING_ITEM,
    CHOOSING_WRAP_COLOR,
    CHOOSING_FILLING,
    CHOOSING_RIBBON_COLOR_BOUQUET,
    TYPING_COLOR_PREFERENCES,
    TYPING_PRICE_BOUQUET,
    CHOOSING_SET_FILLING,
    CHOOSING_RIBBON_COLOR_SET,
    TYPING_PRICE_SET,
    CONFIRMING
) = range(11)

load_dotenv()

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID"))

# === Каталог ===
CATEGORIES = {
    "bouquets": {
        "name": "Букеты💐",
        "items": {
            "b1": "Новогодний букет🎄",
            "b2": "Букет на день рождения🥳",
            "b3": "Букет для второй половинки❤️",
            "b4": "Букет для отчаянных с лакрицей🌚🌝"
        }
    },
    "sets": {
        "name": "Наборы🎁",
        "items": {
            "s1": "Новогодний набор🎆",
            "s2": "Набор на день рождения🎂",
            "s3": "Набор 'Смелый' с добавлением лакрицы😎",
            "s4": "Набор 'Самый смелый' с добавлением острого мармелада🔥"
        }
    }
}

WRAP_COLORS = {
    "black": "Чёрная",
    "white-blue": "Светло-голубая",
    "newhite": "Белая новогодняя",
    "negreen": "Зелёная новогодняя",
    "pink": "Розовая",
    "blue": "Синяя",
    "darkgreen": "Зелёная"
}

FILLINGS = {
    "sourB": "Кислый букет😵‍💫",
    "sweetB": "Сладкий букет🥹",
    "sweet-sourB": "Кисло-сладкий букет🤔",
    "sweet-lacritsaB": "Сладкий букет с добавлением лакрицы😳"
}

SET_FILLINGS = {
    "sourS": "Кислый набор😵‍💫",
    "sweetS": "Сладкий набор🥹",
    "sweet-sourS": "Кисло-сладкий набор🤔",
    "lacritsaS": "Набор с лакрицей😎",
    "sweet-lacritsaS": "Сладкий с лакрицей😳",
    "spicy-lacritsaS": "Острый набор с лакрицей🔥"
}

SET_FILLING_RULES = {
    "s1": ["sweetS", "sourS", "sweet-sourS"],
    "s2": ["sweetS", "sourS", "sweet-sourS"],
    "s3": ["lacritsaS", "sweet-lacritsaS"],
    "s4": ["spicy-lacritsaS"]
}

RIBBON_COLORS = {
    "yellow": "Жёлтая",
    "wblue": "Голубая",
    "burgundy": "Бордовая",
    "pink": "Розовая",
    "wlilac": "Светло-сиреневая",
    "orange": "Оранжевая",
    "crimson": "Малиновая",
    "purple": "Фиолетовая",
    "green": "Зелёная",
    "lilac": "Сиреневая",
    "ferrari": "Ferrari",
    "negreen": "Тёмно-зеленая новогодняя",
    "negold": "Золотая новогодняя",
    "negreengold": "Новогодняя зелёное золото",
    "neredgold": "Новогодняя красное золото",
    "nepurplegold": "Новогодняя фиолетовое золото"
}

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def build_category_keyboard():
    return [
        [InlineKeyboardButton("Букеты💐", callback_data="category_bouquets"),
         InlineKeyboardButton("Наборы🎁", callback_data="category_sets")]
    ]

def build_back_to_categories_button():
    return [InlineKeyboardButton("← Назад к категориям", callback_data="back_to_categories")]

def build_back_to_bouquets_button():
    return [InlineKeyboardButton("← Назад к букетам", callback_data="back_to_bouquets")]

def build_back_to_sets_button():
    return [InlineKeyboardButton("← Назад к наборам", callback_data="back_to_sets")]

def build_item_keyboard(category_key):
    items = CATEGORIES[category_key]["items"]
    keyboard = [[InlineKeyboardButton(name, callback_data=f"item_{key}")] for key, name in items.items()]
    keyboard.append(build_back_to_categories_button())
    return keyboard

# === ОБРАБОТЧИКИ ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здравствуйте!")
    reply_markup = InlineKeyboardMarkup(build_category_keyboard())
    await update.message.reply_text("Выберите, что вас интересует:", reply_markup=reply_markup)
    return CHOOSING_CATEGORY

async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_categories":
        reply_markup = InlineKeyboardMarkup(build_category_keyboard())
        await query.edit_message_text("Выберите, что вас интересует:", reply_markup=reply_markup)
        return CHOOSING_CATEGORY

    if data.startswith("category_"):
        category_key = data.split("_", 1)[1]
        context.user_data["category"] = category_key
        keyboard = build_item_keyboard(category_key)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите позицию:", reply_markup=reply_markup)
        return CHOOSING_ITEM

    return CHOOSING_CATEGORY

async def choose_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_categories":
        reply_markup = InlineKeyboardMarkup(build_category_keyboard())
        await query.edit_message_text("Выберите, что вас интересует:", reply_markup=reply_markup)
        return CHOOSING_CATEGORY

    if data.startswith("item_"):
        item_key = data.split("_", 1)[1]
        category_key = context.user_data.get("category")
        if not category_key or category_key not in CATEGORIES:
            await query.edit_message_text("Ошибка. Начните с /start.")
            return ConversationHandler.END

        item_name = CATEGORIES[category_key]["items"][item_key]
        context.user_data.update({"item_key": item_key, "item_name": item_name})

        if category_key == "bouquets":
            photo_path = "Photos/wraps_overview.jpg"
            if os.path.exists(photo_path):
                with open(photo_path, "rb") as photo:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption="🎀 Выберите цвет обёртки:",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton(name, callback_data=f"wrap_{key}")]
                            for key, name in WRAP_COLORS.items()
                        ] + [build_back_to_bouquets_button()])
                    )
            else:
                await update.effective_message.reply_text(
                    "🎀 Выберите цвет обёртки:",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(name, callback_data=f"wrap_{key}")]
                        for key, name in WRAP_COLORS.items()
                    ] + [build_back_to_bouquets_button()])
                )
            try:
                await query.message.delete()
            except:
                pass
            return CHOOSING_WRAP_COLOR

        elif category_key == "sets":
            allowed_fills = SET_FILLING_RULES.get(item_key, list(SET_FILLINGS.keys()))
            keyboard = [
                [InlineKeyboardButton(SET_FILLINGS[key], callback_data=f"setfill_{key}")]
                for key in allowed_fills if key in SET_FILLINGS
            ]
            if not keyboard:
                await query.edit_message_text("❌ Нет доступных вариантов наполнения.")
                return ConversationHandler.END
            keyboard.append(build_back_to_sets_button())
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("🍬 Выберите наполнение набора:", reply_markup=reply_markup)
            return CHOOSING_SET_FILLING

    return CHOOSING_ITEM

# --- ПУТЬ ДЛЯ БУКЕТОВ ---
async def choose_wrap_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        await query.message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение с обёрткой: {e}")

    if query.data == "back_to_bouquets":
        keyboard = build_item_keyboard("bouquets")
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.effective_chat.send_message("Выберите букет:", reply_markup=reply_markup)
        return CHOOSING_ITEM

    if query.data.startswith("wrap_"):
        key = query.data.split("_", 1)[1]
        if key not in WRAP_COLORS:
            return CHOOSING_WRAP_COLOR
        context.user_data["wrap_color"] = WRAP_COLORS[key]
        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"fillb_{k}")]
            for k, name in FILLINGS.items()
        ]
        keyboard.append(build_back_to_bouquets_button())
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.effective_chat.send_message("🌿 Выберите наполнение букета:", reply_markup=reply_markup)
        return CHOOSING_FILLING

    return CHOOSING_WRAP_COLOR

async def choose_filling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_bouquets":
        keyboard = build_item_keyboard("bouquets")
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await query.message.delete()
        except:
            pass
        await update.effective_chat.send_message("Выберите букет:", reply_markup=reply_markup)
        return CHOOSING_ITEM

    if data.startswith("fillb_"):
        key = data.split("_", 1)[1]
        if key not in FILLINGS:
            return CHOOSING_FILLING
        context.user_data["filling"] = FILLINGS[key]
        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"ribbonb_{k}")]
            for k, name in RIBBON_COLORS.items()
        ]
        keyboard.append(build_back_to_bouquets_button())

        photo_path = "Photos/ribbon_overview.png"
        if os.path.exists(photo_path):
            with open(photo_path, "rb") as photo:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo,
                    caption="🎀 Выберите цвет подарочной ленты:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        else:
            await update.effective_chat.send_message(
                "🎀 Выберите цвет подарочной ленты:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        try:
            await query.message.delete()
        except:
            pass
        return CHOOSING_RIBBON_COLOR_BOUQUET

    return CHOOSING_FILLING

async def choose_ribbon_color_bouquet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        await query.message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение с лентой: {e}")

    if query.data == "back_to_bouquets":
        keyboard = build_item_keyboard("bouquets")
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.effective_chat.send_message("Выберите букет:", reply_markup=reply_markup)
        return CHOOSING_ITEM

    if query.data.startswith("ribbonb_"):
        key = query.data.split("_", 1)[1]
        if key not in RIBBON_COLORS:
            return CHOOSING_RIBBON_COLOR_BOUQUET
        context.user_data["ribbon_color"] = RIBBON_COLORS[key]
        await update.effective_chat.send_message("🎨 Напишите пожелания по цветовой палитре (например: «Нежные пастельные тона»):")
        return TYPING_COLOR_PREFERENCES

    return CHOOSING_RIBBON_COLOR_BOUQUET

async def receive_color_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    color_pref = update.message.text
    context.user_data["color_preferences"] = color_pref
    await update.message.reply_text("💰 Укажите желаемую цену букета (не менее 1000руб!):")
    return TYPING_PRICE_BOUQUET

async def receive_price_bouquet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = update.message.text.strip()
    context.user_data["price"] = price

    item = context.user_data["item_name"]
    summary = (
        f"📦 Вы выбрали:\n\n"
        f"• Товар: {item}\n"
        f"• Обёртка: {context.user_data['wrap_color']}\n"
        f"• Наполнение: {context.user_data['filling']}\n"
        f"• Лента: {context.user_data['ribbon_color']}\n"
        f"• Палитра: _{context.user_data['color_preferences']}_\n"
        f"• Желаемая цена: {price}\n\n"
        f"✅ Подтвердить заказ?"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Да, всё верно", callback_data="confirm_final")],
        [InlineKeyboardButton("❌ Начать заново", callback_data="restart")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(summary, reply_markup=reply_markup, parse_mode="Markdown")
    return CONFIRMING

# --- ПУТЬ ДЛЯ НАБОРОВ ---
async def choose_set_filling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        await query.message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение с наполнением набора: {e}")

    if query.data == "back_to_sets":
        keyboard = build_item_keyboard("sets")
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.effective_chat.send_message("Выберите набор:", reply_markup=reply_markup)
        return CHOOSING_ITEM

    if query.data.startswith("setfill_"):
        key = query.data.split("_", 1)[1]
        if key not in SET_FILLINGS:
            return CHOOSING_SET_FILLING
        context.user_data["set_filling"] = SET_FILLINGS[key]

        # ИСПРАВЛЕНО: путь к фото — без Jarvis/
        photo_path = "Photos/ribbon_overview.png"
        if os.path.exists(photo_path):
            with open(photo_path, "rb") as photo:
                keyboard = [
                    [InlineKeyboardButton(name, callback_data=f"ribbons_{key}")]
                    for key, name in RIBBON_COLORS.items()
                ]
                keyboard.append(build_back_to_sets_button())
                reply_markup = InlineKeyboardMarkup(keyboard)

                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo,
                    caption="🎀 Выберите цвет подарочной ленты:",
                    reply_markup=reply_markup
                )
        else:
            keyboard = [
                [InlineKeyboardButton(name, callback_data=f"ribbons_{key}")]
                for key, name in RIBBON_COLORS.items()
            ]
            keyboard.append(build_back_to_sets_button())
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.effective_chat.send_message(
                "🎀 Выберите цвет подарочной ленты:",
                reply_markup=reply_markup
            )
        return CHOOSING_RIBBON_COLOR_SET

    return CHOOSING_SET_FILLING

async def choose_ribbon_color_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        await query.message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение с лентой: {e}")

    if query.data == "back_to_sets":
        keyboard = build_item_keyboard("sets")
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.effective_chat.send_message("Выберите набор:", reply_markup=reply_markup)
        return CHOOSING_ITEM

    if query.data.startswith("ribbons_"):
        key = query.data.split("_", 1)[1]
        if key not in RIBBON_COLORS:
            return CHOOSING_RIBBON_COLOR_SET
        context.user_data["ribbon_color"] = RIBBON_COLORS[key]
        await update.effective_chat.send_message("💰 Укажите желаемую цену набора (не менее 500 руб):")
        return TYPING_PRICE_SET

    return CHOOSING_RIBBON_COLOR_SET

async def receive_price_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = update.message.text.strip()
    context.user_data["price"] = price

    item = context.user_data["item_name"]
    summary = (
        f"📦 Вы выбрали:\n\n"
        f"• Товар: {item}\n"
        f"• Наполнение: {context.user_data['set_filling']}\n"
        f"• Лента: {context.user_data['ribbon_color']}\n"
        f"• Желаемая цена: {price}\n\n"
        f"✅ Подтвердить заказ?"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Да, всё верно", callback_data="confirm_final")],
        [InlineKeyboardButton("❌ Начать заново", callback_data="restart")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(summary, reply_markup=reply_markup, parse_mode="Markdown")
    return CONFIRMING

# --- ПОДТВЕРЖДЕНИЕ ---
async def confirm_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "restart":
        await query.edit_message_text("Чтобы начать заново, отправьте команду /start.")
        return ConversationHandler.END

    if data == "confirm_final":
        user = update.effective_user
        ud = context.user_data
        category = ud["category"]

        if category == "bouquets":
            details = (
                f"Товар: {ud['item_name']}\n"
                f"Обёртка: {ud['wrap_color']}\n"
                f"Наполнение: {ud['filling']}\n"
                f"Лента: {ud['ribbon_color']}\n"
                f"Палитра: _{ud['color_preferences']}_\n"
                f"Желаемая цена: {ud['price']}\n"
            )
        else:
            details = (
                f"Товар: {ud['item_name']}\n"
                f"Наполнение: {ud['set_filling']}\n"
                f"Лента: {ud['ribbon_color']}\n"
                f"Желаемая цена: {ud['price']}\n"
            )

        order_info = (
            f"📦 *Новый заказ!*\n\n"
            f"Пользователь: {user.full_name} (@{user.username or 'нет'})\n"
            f"ID: `{user.id}`\n\n"
            f"{details}"
        )

        await query.edit_message_text("✅ Ваш заказ принят!\nМенеджер свяжется с вами в ближайшее время.")

        try:
            await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=order_info, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Ошибка отправки менеджеру: {e}")

        return ConversationHandler.END

    return CONFIRMING

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Заказ отменён. Отправьте /start, чтобы начать заново.")
    return ConversationHandler.END

# === ЗАПУСК ===
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_CATEGORY: [CallbackQueryHandler(choose_category)],
            CHOOSING_ITEM: [CallbackQueryHandler(choose_item)],
            CHOOSING_WRAP_COLOR: [CallbackQueryHandler(choose_wrap_color)],
            CHOOSING_FILLING: [CallbackQueryHandler(choose_filling)],
            CHOOSING_RIBBON_COLOR_BOUQUET: [CallbackQueryHandler(choose_ribbon_color_bouquet)],
            TYPING_COLOR_PREFERENCES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_color_preferences)],
            TYPING_PRICE_BOUQUET: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_price_bouquet)],
            CHOOSING_SET_FILLING: [CallbackQueryHandler(choose_set_filling)],
            CHOOSING_RIBBON_COLOR_SET: [CallbackQueryHandler(choose_ribbon_color_set)],
            TYPING_PRICE_SET: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_price_set)],
            CONFIRMING: [CallbackQueryHandler(confirm_final)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

    application.add_handler(conv_handler)

    # === ЗАПУСК ТОЛЬКО WEBHOOK ===
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    PORT = int(os.environ.get("PORT", 8000))

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )
    # ← НИКАКОГО run_polling() НЕТ! ←


if __name__ == "__main__":
    main()