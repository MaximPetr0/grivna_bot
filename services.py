from datetime import datetime, timedelta
from sqlalchemy import select
from database import SessionLocal
from models import Expense
from html import escape


def parse_message(text):
    parts = text.rsplit(" ", 1)
    if len(parts) != 2:
        return None

    category, amount_text = parts
    try:
        amount = float(amount_text.replace(",", "."))
    except ValueError:
        return None

    return category.strip().lower(), amount


def add_expense(user_id, category, amount):
    with SessionLocal() as session:
        expense = Expense(user_id=user_id, category=category, amount=amount)
        session.add(expense)
        session.commit()


def get_expenses(user_id, start, end):
    with SessionLocal() as session:
        query = select(Expense).where(
            Expense.user_id == user_id,
            Expense.created_at >= start,
            Expense.created_at < end,
        )
        return session.scalars(query).all()


def get_day(user_id, day):
    start = datetime(day.year, day.month, day.day)
    end = start + timedelta(days=1)
    return get_expenses(user_id, start, end)


def get_month(user_id, year, month):
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    return get_expenses(user_id, start, end)


def make_category_report(expenses, category):
    items = [e for e in expenses if e.category == category]

    if not items:
        return "Трат нет 🎉"

    lines = []
    for e in items:
        lines.append(f"• {e.created_at:%d.%m} — {e.amount:.2f} грн")

    total = sum(e.amount for e in items)
    lines.append("")
    lines.append(f"💰 <b>Итого: {total:.2f} грн</b> ({len(items)} раз)")
    return "\n".join(lines)


def parse_month(text):
    try:
        d = datetime.strptime(text, "%Y-%m")
    except ValueError:
        return None
    return d.year, d.month


def make_report(expenses):
    if not expenses:
        return "Трат нет 🎉"

    totals = {}
    for e in expenses:
        totals[e.category] = totals.get(e.category, 0) + e.amount

    total = sum(totals.values())
    sorted_totals = sorted(totals.items(), key=lambda item: item[1], reverse=True)

    lines = []
    for category, amount in sorted_totals:
        percent = amount / total * 100
        lines.append(f"• {escape(category)} — <b>{amount:.2f}</b> грн ({percent:.0f}%)")

    lines.append("")
    lines.append(f"💰 <b>Итого: {total:.2f} грн</b>")
    return "\n".join(lines)


def delete_last(user_id):
    with SessionLocal() as session:
        query = (
            select(Expense)
            .where(Expense.user_id == user_id)
            .order_by(Expense.id.desc())
            .limit(1)
        )
        expense = session.scalars(query).first()

        if expense is None:
            return None

        category, amount = expense.category, expense.amount
        session.delete(expense)
        session.commit()
        return category, amount
