import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd

from src.services import (
    cashback_categories,
    investment_bank,
    phone_number_search,
    simple_search,
    transfer_to_persons,
)


def make_df():
    return pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                [
                    "2021-12-01 10:00:00",
                    "2021-12-05 12:00:00",
                    "2021-12-10 18:30:00",
                    "2021-03-15 09:00:00",
                    "2021-03-20 11:00:00",
                ]
            ),
            "Номер карты": ["*7197", "*7197", "", "*4556", "*4556"],
            "Сумма платежа": [-160.89, -64.00, -800.00, -943.50, -295.32],
            "Категория": [
                "Супермаркеты",
                "Супермаркеты",
                "Переводы",
                "Переводы",
                "Развлечения",
            ],
            "Описание": ["Колхоз", "Магнит", "Константин Л.", "Дмитрий Ш.", "Кинотеатр"],
        }
    )


def make_list():
    return [
        {"Дата операции": "01.12.2021 10:00:00", "Сумма платежа": -160.89},
        {"Дата операции": "05.12.2021 12:00:00", "Сумма платежа": -64.00},
        {"Дата операции": "10.12.2021 18:30:00", "Сумма платежа": 5000.00},
    ]


def test_cashback_categories():
    result = cashback_categories(make_df(), 2021, 12)
    assert result["Супермаркеты"] == 2.25
    assert result["Переводы"] == 8.0


def test_investment_bank_limit_10():
    assert investment_bank("2021-12", make_list(), 10) == 15.11


def test_investment_bank_no_income():
    assert investment_bank("2021-12", make_list(), 50) == 75.11


def test_investment_bank_wrong_month():
    assert investment_bank("2021-11", make_list(), 10) == 0.0


def test_simple_search():
    result = simple_search(make_df(), "колхоз")
    assert len(result) == 1
    assert result[0]["Описание"] == "Колхоз"


def test_phone_number_search():
    df = make_df()
    df.loc[len(df)] = {
        "Дата операции": pd.Timestamp("2021-12-20 14:00:00"),
        "Номер карты": "*7197",
        "Сумма платежа": -100.0,
        "Категория": "Связь",
        "Описание": "МТС +7 9 195 555-33-22",
    }
    result = phone_number_search(df)
    assert len(result) == 1


def test_transfer_to_persons():
    result = transfer_to_persons(make_df(), "Q4")
    assert len(result) == 1
    assert result[0]["Описание"] == "Константин Л."
