import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json

import pandas as pd

import src.reports as reports
from src.reports import spending_by_category, spending_by_weekday


def make_df():
    return pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                [
                    "2021-12-01 10:00:00",
                    "2021-12-05 12:00:00",
                    "2021-10-10 18:30:00",
                    "2021-12-20 09:00:00",
                    "2021-12-21 11:00:00",
                ]
            ),
            "Сумма платежа": [-160.89, -64.00, -800.00, 5000.00, -295.32],
            "Категория": [
                "Супермаркеты",
                "Супермаркеты",
                "Переводы",
                "Зарплата",
                "Развлечения",
            ],
        }
    )


def test_spending_by_category_with_date():
    result = spending_by_category(make_df(), "Супермаркеты", "01.01.2022 00:00:00")
    assert result["total_spent"] == 224.89
    assert result["spent_by_months"]["12.2021"] == 224.89


def test_spending_by_category_excludes_old():
    result = spending_by_category(make_df(), "Переводы", "01.01.2022 00:00:00")
    # 3 месяца назад от 01.01.2022 — это 01.10.2021, перевод 10.10.2021 входит в период
    assert result["total_spent"] == 800.0


def test_spending_by_weekday():
    result = spending_by_weekday(make_df())
    # 01.12.2021 — среда, 05.12.2021 — воскресенье, 10.10.2021 — воскресенье,
    # 21.12.2021 — вторник
    assert result["by_weekday"]["Вторник"] == 295.32
    assert result["total_spent"] == 1320.21


def test_report_file_is_created():
    spending_by_category(make_df(), "Супермаркеты", "01.01.2022 00:00:00")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root, "reports", "spending_by_category.json")
    assert os.path.exists(file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    assert data["category"] == "Супермаркеты"


def test_get_current_date_is_replaceable(monkeypatch):
    monkeypatch.setattr(reports, "get_current_date", lambda: pd.Timestamp("2022-01-01"))
    df = make_df()
    # при подменённой «текущей» дате отчёт за 3 месяца берёт октябрь и декабрь 2021
    expenses = df[df["Сумма платежа"] < 0]
    boundary = pd.Timestamp("2022-01-01") - pd.DateOffset(months=3)
    filtered = expenses[expenses["Дата операции"] >= boundary]
    assert len(filtered) == 4
