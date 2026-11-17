"""Сервисы на функциональном программировании: кешбэк, инвесткопилка, поиск, переводы."""
import json
import logging
import re
from functools import wraps
from typing import Any, Callable, Dict, List

import pandas as pd

from src.utils import get_transactions_list as read_transactions_dict

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def log_service(func: Callable) -> Callable:
    """Декоратор: логирует имя сервиса и размер результата."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("Запуск сервиса %s", func.__name__)
        result = func(*args, **kwargs)
        try:
            logger.info("Сервис %s вернул %d записей", func.__name__, len(result))
        except TypeError:
            logger.info("Сервис %s вернул %s", func.__name__, result)
        return result

    return wrapper


def filter_by_period(df: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
    """Чистая функция: фильтрует транзакции по году и месяцу."""
    dates = df["Дата операции"]
    return df[(dates.dt.year == year) & (dates.dt.month == month)]


@log_service
def cashback_categories(df: pd.DataFrame, year: int, month: int) -> Dict[str, float]:
    """Сервис «Кэшбэк»: кешбэк 1% по каждой категории за месяц."""
    month_df = filter_by_period(df, year, month)
    expenses = month_df[month_df["Сумма платежа"] < 0]
    expenses = expenses.assign(cashback=lambda d: d["Сумма платежа"].abs() * 0.01)
    grouped = expenses.groupby("Категория")["cashback"].sum()
    return {category: round(float(value), 2) for category, value in grouped.items()}


def get_transaction_period(transaction: Dict[str, Any]) -> pd.Period:
    """Чистая функция: возвращает месяц транзакции как pd.Period."""
    return pd.Period(
        pd.to_datetime(transaction["Дата операции"], format="%d.%m.%Y %H:%M:%S"), freq="M"
    )


@log_service
def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Сервис «Инвесткопилка»: сумма округлений трат до limit за месяц."""
    month_period = pd.Period(month, freq="M")
    monthly = filter(lambda t: get_transaction_period(t) == month_period, transactions)
    spent = map(lambda t: abs(float(t["Сумма платежа"])), monthly)
    expenses_only = filter(lambda s: s > 0, spent)
    rounded = map(lambda s: (limit - s % limit) % limit, expenses_only)
    return round(sum(rounded), 2)


@log_service
def simple_search(df: pd.DataFrame, search_string: str) -> List[Dict[str, Any]]:
    """Сервис «Простой поиск»: ищет строку в описании и категории."""
    pattern = re.compile(re.escape(search_string), re.IGNORECASE)
    matches = df[
        df["Описание"].apply(lambda text: bool(pattern.search(str(text))))
        | df["Категория"].apply(lambda text: bool(pattern.search(str(text))))
    ]
    return matches.to_dict("records")


@log_service
def phone_number_search(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Сервис «Поиск по номеру телефона»: находит +7 Х ХХХ ХХХ-ХХ-ХХ в описаниях."""
    pattern = re.compile(r"\+7\s\d\s\d{3}\s\d{3}-\d{2}-\d{2}")
    matches = df[df["Описание"].apply(lambda text: bool(pattern.search(str(text))))]
    return matches.to_dict("records")


@log_service
def transfer_to_persons(df: pd.DataFrame, quarter: str = "Q1") -> List[Dict[str, Any]]:
    """Сервис «Переводы физлицам»: переводы не своим счетам за квартал."""
    quarter_num = int(quarter.strip("Qq"))
    quarter_df = df[df["Дата операции"].dt.quarter == quarter_num]
    transfers = quarter_df[quarter_df["Категория"] == "Переводы"]
    persons = transfers[
        transfers["Описание"].apply(
            lambda text: bool(re.search(r"[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.", str(text)))
        )
    ]
    persons = persons[
        ~persons["Описание"].str.contains("Свой счёт", case=False, na=False)
    ]
    return persons.to_dict("records")


def investment_bank_report(
    month: str, limit: int, transactions: List[Dict[str, Any]] = None
) -> str:
    """Обёртка «Инвесткопилки» в формате JSON для проверки."""
    if transactions is None:
        transactions = read_transactions_dict()
    saved = investment_bank(month, transactions, limit)
    return json.dumps({"month": month, "limit": limit, "saved": saved}, ensure_ascii=False)
