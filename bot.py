# pip install python-telegram-bot==20.7 python-dotenv
import os, json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")                         # токен из BotFather
WEBAPP_URL = os.getenv("WEBAPP_URL")                   # https://<username>.github.io/<repo>/
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))   # твой chat_id (см. ниже)

def humanize(choice: dict) -> str:
    day_map = {"thu":"вечер четверга", "fri":"вечер пятницы", "wknd":"выходные"}
    mode_map = {"museum":"Сенсориум", "dinner":"ужин"}
    mode = mode_map.get(choice.get("mode", ""), "—")
    day  = day_map.get(choice.get("day", ""), "—")
    return f"{mode}, {day}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("Открыть квест", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text("Небольшой квест на 2–3 минуты", reply_markup=InlineKeyboardMarkup(kb))

# Приём данных из Mini App (sendData)
async def on_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.web_app_data:
        return

    # Данные от страницы
    try:
        data = json.loads(update.message.web_app_data.data)
    except Exception:
        data = {}

    # Сообщение для неё
    if data.get("type") == "sensorium_choice":
        day_map = {"thu":"в четверг вечером", "fri":"в пятницу вечером", "wknd":"на выходных"}
        mode_map = {"museum":"в музей темноты — Сенсориум", "dinner":"на ужин"}
        day_h = day_map.get(data.get("day",""), "")
        mode_h = mode_map.get(data.get("mode",""), "")
        text_for_user = f"Жду с нетерпением\nУвидимся {day_h}\n{mode_h}" if mode_h else f"Жду с нетерпением\nУвидимся {day_h}"
        await update.message.reply_text(text_for_user)

        # Уведомление тебе
        if ADMIN_CHAT_ID:
            user = update.effective_user
            who = f"{user.full_name} (@{user.username})" if user else "кто-то"
            summary = humanize(data)
            msg = f"Выбор: {summary}\nОт: {who} (chat_id {update.effective_chat.id})"
            try:
                await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
            except Exception:
                pass

# Вспомогательная команда, чтобы узнать свой chat_id для ADMIN_CHAT_ID
async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ваш chat_id: {update.effective_chat.id}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("me", me))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, on_webapp))
    app.run_polling()

if __name__ == "__main__":
    main()

