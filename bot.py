import os
from datetime import date
from html import escape
import telebot
from dotenv import load_dotenv
from services import parse_message, add_expense, get_day, get_month, make_report, delete_last, make_category_report, \
    parse_month

load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))

BTN_TODAY = "📅 Сегодня"
BTN_MONTH = "🗓 Месяц"
BTN_UNDO = "↩️ Отменить"


def main_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(BTN_TODAY, BTN_MONTH)
    markup.row(BTN_UNDO)
    return markup


@bot.message_handler(commands=['skolko'])
def skolko(message):
    args = telebot.util.extract_arguments(message.text)
    if not args:
        bot.reply_to(message, "Пиши так: /skolko кофе или /skolko кофе 2026-09")
        return

    category = args
    t = date.today()
    year, month_num = t.year, t.month

    parts = args.rsplit(" ", 1)
    if len(parts) == 2:
        parsed = parse_month(parts[1])
        if parsed is not None:
            category = parts[0]
            year, month_num = parsed

    category = category.strip().lower()
    expenses = get_month(message.chat.id, year, month_num)
    bot.reply_to(message,
                 f"<b>🔎 {escape(category)} — {month_num:02d}.{year}</b>\n\n"
                 + make_category_report(expenses, category),
                 parse_mode="HTML")


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
                 "Привет! Я grivna_bot 💰\n\n"
                 "Пиши траты так: кофе 80\n"
                 "/skolko кофе — сколько на кофе\n"
                 "Или жми кнопки внизу 👇",
                 reply_markup=main_keyboard())


@bot.message_handler(commands=['today'])
@bot.message_handler(func=lambda m: m.text == BTN_TODAY)
def today(message):
    expenses = get_day(message.chat.id, date.today())
    bot.reply_to(message, "<b>📅 Сегодня</b>\n\n" + make_report(expenses), parse_mode="HTML")


@bot.message_handler(commands=['month'])
@bot.message_handler(func=lambda m: m.text == BTN_MONTH)
def month(message):
    t = date.today()
    expenses = get_month(message.chat.id, t.year, t.month)
    bot.reply_to(message, "<b>🗓 Этот месяц</b>\n\n" + make_report(expenses), parse_mode="HTML")


@bot.message_handler(commands=['undo'])
@bot.message_handler(func=lambda m: m.text == BTN_UNDO)
def undo(message):
    result = delete_last(message.chat.id)
    if result is None:
        bot.reply_to(message, "Нечего удалять 🤷")
        return

    category, amount = result
    bot.reply_to(message, f"🗑 Удалил: {category} — {amount:.2f} грн")


@bot.message_handler(content_types=['text'])
def expense(message):
    result = parse_message(message.text)
    if result is None:
        bot.reply_to(message, "Не понял 🤔 Пиши так: кофе 80")
        return

    category, amount = result
    add_expense(message.chat.id, category, amount)
    bot.reply_to(message, f"✅ Записал: {category} — {amount:.2f} грн")


bot.set_my_commands([
    telebot.types.BotCommand("start", "Начать"),
    telebot.types.BotCommand("today", "Траты за сегодня"),
    telebot.types.BotCommand("month", "Траты за месяц"),
    telebot.types.BotCommand("undo", "Удалить последнюю трату"),
    telebot.types.BotCommand("skolko", "Траты на категорию")
])
print("Бот запущен...")
bot.infinity_polling()
