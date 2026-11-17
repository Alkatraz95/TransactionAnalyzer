"""Точка входа: интерфейс командной строки для страниц и сервисов приложения."""
import argparse
import sys

from src.reports import spending_by_category, spending_by_weekday
from src.services import (
    cashback_categories,
    investment_bank_report,
    phone_number_search,
    simple_search,
    transfer_to_persons,
)
from src.utils import read_transactions
from src.views import events_page, main_page


def run_main_page(args) -> None:
    """Запускает главную страницу и печатает JSON."""
    df = read_transactions()
    print(main_page(args.datetime, df))


def run_events_page(args) -> None:
    """Запускает страницу «События» и печатает JSON."""
    df = read_transactions()
    print(events_page(args.datetime, args.period, df))


def run_cashback(args) -> None:
    """Запускает сервис «Кэшбэк» и печатает JSON."""
    df = read_transactions()
    print(cashback_categories(df, args.year, args.month))


def run_investment_bank(args) -> None:
    """Запускает сервис «Инвесткопилка» и печатает JSON."""
    print(investment_bank_report(args.month, args.limit))


def run_search(args) -> None:
    """Запускает сервис «Простой поиск» и печатает JSON."""
    df = read_transactions()
    print(simple_search(df, args.query))


def run_phone(args) -> None:
    """Запускает сервис «Поиск по номеру телефона» и печатает JSON."""
    df = read_transactions()
    print(phone_number_search(df))


def run_transfers(args) -> None:
    """Запускает сервис «Переводы физлицам» и печатает JSON."""
    df = read_transactions()
    print(transfer_to_persons(df, args.quarter))


def run_category_report(args) -> None:
    """Запускает отчёт «Траты по категории» (результат также пишется в файл)."""
    df = read_transactions()
    print(spending_by_category(df, args.category, args.date))


def run_weekday_report(args) -> None:
    """Запускает отчёт «Траты по дням недели» (результат также пишется в файл)."""
    df = read_transactions()
    print(spending_by_weekday(df, args.date))


def build_parser() -> argparse.ArgumentParser:
    """Собирает парсер командной строки."""
    parser = argparse.ArgumentParser(
        prog="main",
        description="Веб-приложение «Транзакции»: страницы и сервисы",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    main_parser = subparsers.add_parser("main_page")
    main_parser.add_argument("--datetime", required=True, help="YYYY-MM-DD HH:MM:SS")
    main_parser.set_defaults(func=run_main_page)

    events_parser = subparsers.add_parser("events_page")
    events_parser.add_argument("--datetime", required=True, help="YYYY-MM-DD HH:MM:SS")
    events_parser.add_argument("--period", default="M", choices=["W", "M", "Y", "ALL"])
    events_parser.set_defaults(func=run_events_page)

    cashback_parser = subparsers.add_parser("cashback")
    cashback_parser.add_argument("--year", type=int, required=True)
    cashback_parser.add_argument("--month", type=int, required=True)
    cashback_parser.set_defaults(func=run_cashback)

    investment_parser = subparsers.add_parser("investment_bank")
    investment_parser.add_argument("--month", required=True, help="YYYY-MM")
    investment_parser.add_argument("--limit", type=int, required=True, choices=[10, 50, 100])
    investment_parser.set_defaults(func=run_investment_bank)

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--query", required=True)
    search_parser.set_defaults(func=run_search)

    subparsers.add_parser("phone").set_defaults(func=run_phone)

    transfers_parser = subparsers.add_parser("transfers")
    transfers_parser.add_argument("--quarter", default="Q1", choices=["Q1", "Q2", "Q3", "Q4"])
    transfers_parser.set_defaults(func=run_transfers)

    category_parser = subparsers.add_parser("category_report")
    category_parser.add_argument("--category", required=True)
    category_parser.add_argument("--date", default=None, help="DD.MM.YYYY HH:MM:SS")
    category_parser.set_defaults(func=run_category_report)

    weekday_parser = subparsers.add_parser("weekday_report")
    weekday_parser.add_argument("--date", default=None, help="DD.MM.YYYY HH:MM:SS")
    weekday_parser.set_defaults(func=run_weekday_report)

    return parser


def main() -> None:
    """Разбирает аргументы и запускает нужную команду."""
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
