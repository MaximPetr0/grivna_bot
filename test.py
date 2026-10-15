from datetime import date

from services import parse_message, add_expense, make_report, get_day, get_month

USER_ID = 1  # временно вместо message.chat.id

while True:
    text = input("Расход, 'сегодня', 'месяц' или 'выход': ")
    if text == "выход":
        break

    if text == "сегодня":
        print(make_report(get_day(USER_ID, date.today())))
        continue

    if text == "месяц":
        today = date.today()
        print(make_report(get_month(USER_ID, today.year, today.month)))
        continue

    result = parse_message(text)
    if result is None:
        print("Не понял ️🤷‍♂️. Пиши так: кофе 80")
        continue

    category, amount = result
    add_expense(USER_ID, category, amount)
    print(f"✅ Записал: {category} — {amount} грн")