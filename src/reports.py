"""Отчёты: траты по категории и по дням недели, с декоратором записи в файл."""
import json
import logging
import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(ROOT_DIR, "reports")


def save_report(func: Callable) -> Callable:
    """Декоратор: записывает результат отчёта в JSON-файл в папку reports."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        os.makedirs(REPORTS_DIR, exist_ok=True)
        file_name = os.path.join(REPORTS_DIR, f"{func.__name__}.json")
        try:
            result = func(*args, **kwargs)
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump(result, file, ensure_ascii=False, indent=2)
            logger.info("Отчёт сохранён: %s", file_name)
            return result
        except Exception as error:
            logger.error("Ошибка в отчёте %s: %s", func.__name__, error)
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump({"error": str(error)}, file, ensure_ascii=False)
            raise

    return wrapper


def get_current_date() -> datetime:
    """Возвращает «текущую» дату. Отдельная функция, чтобы подменять в тестах."""
    return datetime.now()


@save_report
def spending_by_category(
    df: pd.DataFrame, category: str, date: Optional[str] = None
) -> Dict[str, Any]:
    """Отчёт «Траты по категории» за последние 3 месяца от переданной даты."""
    if date is None:
        end = get_current_date()
    else:
        end = pd.to_datetime(date, format="%d.%m.%Y %H:%M:%S")
    start = end - pd.DateOffset(months=3)

    month_df = df[(df["Дата операции"] >= start) & (df["Дата операции"] <= end)]
    expenses = month_df[month_df["Сумма платежа"] < 0]
    category_df = expenses[expenses["Категория"] == category]

    total = round(float(category_df["Сумма платежа"].abs().sum()), 2)
    by_months = (
        category_df.assign(месяц=category_df["Дата операции"].dt.strftime("%m.%Y"))
        .groupby("месяц")["Сумма платежа"].sum()
        .apply(lambda v: round(abs(float(v)), 2))
        .to_dict()
    )
    return {
        "category": category,
        "total_spent": total,
        "spent_by_months": by_months,
        "period_start": start.strftime("%d.%m.%Y"),
        "period_end": end.strftime("%d.%m.%Y"),
    }


@save_report
def spending_by_weekday(df: pd.DataFrame, date: Optional[str] = None) -> Dict[str, Any]:
    """Отчёт «Сумма трат по дням недели» за всё время наблюдений."""
    weekdays = [
        "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"
    ]
    expenses = df[df["Сумма платежа"] < 0].copy()
    expenses["weekday"] = expenses["Дата операции"].dt.day_of_week
    grouped = expenses.groupby("weekday")["Сумма платежа"].sum().abs()
    by_weekday = {weekdays[i]: round(float(grouped.get(i, 0.0)), 2) for i in range(7)}
    return {"total_spent": round(float(grouped.sum()), 2), "by_weekday": by_weekday}
