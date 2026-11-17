import json

import pandas as pd

from src.views import get_greeting, get_cards, get_top_transactions, main_page


def make_df():
    return pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                ["2021-12-01 10:00:00", "2021-12-05 12:00:00", "2021-12-10 18:30:00"]
            ),
            "Номер карты": ["*7197", "*7197", ""],
            "Сумма платежа": [-160.89, -64.00, -800.00],
            "Категория": ["Супермаркеты", "Супермаркеты", "Переводы"],
            "Описание": ["Колхоз", "Магнит", "Константин Л."],
        }
    )


def test_greeting_day():
    assert get_greeting(pd.Timestamp("2021-12-01 12:00:00")) == "Добрый день"


def test_greeting_night():
    assert get_greeting(pd.Timestamp("2021-12-01 23:30:00")) == "Доброй ночи"


def test_cards():
    cards = get_cards(make_df())
    assert len(cards) == 1
    assert cards[0]["last_digits"] == "7197"
    assert cards[0]["total_spent"] == 224.89
    assert cards[0]["cashback"] == 2.25


def test_top_transactions_five():
    df = make_df()
    assert len(get_top_transactions(df, 5)) == 3


def test_main_page_json_structure():
    result = json.loads(main_page("2021-12-10 18:30:00", make_df()))
    for key in ["greeting", "cards", "top_transactions", "currency_rates", "stock_prices"]:
        assert key in result


from src.views import events_page, get_date_range, get_expenses, get_income
import pytest
from datetime import datetime


def test_get_date_range_month():
    start, end = get_date_range(datetime(2021, 12, 15, 10, 0, 0), "M")
    assert start.strftime("%d.%m.%Y") == "01.12.2021"
    assert end.strftime("%d.%m.%Y") == "15.12.2021"


def test_get_date_range_week():
    start, end = get_date_range(datetime(2021, 12, 15, 10, 0, 0), "W")
    assert start.strftime("%d.%m.%Y") == "13.12.2021"


def test_get_date_range_year():
    start, end = get_date_range(datetime(2021, 12, 15, 10, 0, 0), "Y")
    assert start.strftime("%d.%m.%Y") == "01.01.2021"


def test_get_date_range_all():
    start, end = get_date_range(datetime(2021, 12, 15, 10, 0, 0), "ALL")
    assert end.strftime("%d.%m.%Y") == "15.12.2021"


def test_get_date_range_unknown_period():
    with pytest.raises(ValueError):
        get_date_range(datetime(2021, 12, 15), "D")


def test_expenses_top7_and_rest():
    df = make_df()
    expenses = get_expenses(df)
    assert expenses["total_amount"] == 1025  # 160.89 + 64.00 + 800.00 = 1024.89 → 1025
    assert expenses["main"][0]["category"] == "Переводы"
    assert expenses["transfers_and_cash"][0]["category"] == "Переводы"


def test_income():
    df = make_df()
    income = get_income(df)
    assert income["total_amount"] == 0  # в тестовых данных нет поступлений


def test_events_page_json_structure():
    result = json.loads(events_page("2021-12-10 18:30:00", "M", make_df()))
    for key in ["expenses", "income", "currency_rates", "stock_prices"]:
        assert key in result
