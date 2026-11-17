"""Функции для генерации JSON-ответов веб-страниц: «Главная» и «События»."""
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from dotenv import load_dotenv

from src.utils import read_transactions

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_FILE = os.path.join(ROOT_DIR, "user_settings.json")


def load_settings() -> Dict[str, Any]:
    """Загружает пользовательские настройки из user_settings.json."""
    with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_greeting(dt: datetime) -> str:
    """Возвращает приветствие в зависимости от времени."""
    hour = dt.hour
    if 6 <= hour < 12:
        return "Доброе утро"
    if 12 <= hour < 18:
        return "Добрый день"
    if 18 <= hour < 23:
        return "Добрый вечер"
    return "Доброй ночи"


def get_cards(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Возвращает информацию по каждой карте: последние 4 цифры, расходы, кешбэк."""
    cards = []
    for card, group in df.groupby("Номер карты"):
        if not card or pd.isna(card):  # переводы без карты пропускаем
            continue
        spent = abs(group[group["Сумма платежа"] < 0]["Сумма платежа"].sum())
        cards.append(
            {
                "last_digits": str(card)[-4:],
                "total_spent": round(float(spent), 2),
                "cashback": round(float(spent) * 0.01, 2),
            }
        )
    return cards


def get_top_transactions(df: pd.DataFrame, n: int = 5) -> List[Dict[str, Any]]:
    """Возвращает топ-n транзакций по сумме платежа."""
    top = df.sort_values("Сумма платежа", key=abs, ascending=False).head(n)
    return [
        {
            "date": row["Дата операции"].strftime("%d.%m.%Y"),
            "amount": round(float(row["Сумма платежа"]), 2),
            "category": row["Категория"],
            "description": row["Описание"],
        }
        for _, row in top.iterrows()
    ]


def get_currency_rates() -> List[Dict[str, Any]]:
    """Возвращает курсы валют: ключ apilayer, резерв — ЦБ РФ."""
    api_key = os.getenv("API_KEY_CURRENCY")
    rates = []
    for currency in load_settings()["user_currencies"]:
        rate = 0.0
        try:
            if api_key:
                response = requests.get(
                    "https://api.apilayer.com/exchangerates_data/latest"
                    f"?base=RUB&symbols={currency}",
                    headers={"apikey": api_key},
                    timeout=5,
                )
                response.raise_for_status()
                rate = round(1 / response.json()["rates"][currency], 2)
            else:
                response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
                response.raise_for_status()
                rate = round(response.json()["Valute"].get(currency, {}).get("Value", 0.0), 2)
        except (
            requests.RequestException, KeyError, ValueError, TypeError, ZeroDivisionError
        ) as error:
            logger.error("Ошибка получения курса %s: %s", currency, error)
        rates.append({"currency": currency, "rate": rate})
    return rates


def get_stock_prices() -> List[Dict[str, Any]]:
    """Возвращает цены акций: ключ FMP, резерв — Yahoo, затем Stooq."""
    api_key = os.getenv("API_KEY_STOCKS")
    prices = []
    for stock in load_settings()["user_stocks"]:
        price = 0.0
        try:
            if api_key:
                response = requests.get(
                    "https://financialmodelingprep.com/api/v3/quote-short/"
                    f"{stock}?apikey={api_key}",
                    timeout=5,
                )
                response.raise_for_status()
                price = float(response.json()[0]["price"])
            else:
                response = requests.get(
                    f"https://query1.finance.yahoo.com/v8/finance/chart/{stock}",
                    timeout=5,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                response.raise_for_status()
                price = float(response.json()["chart"]["result"][0]["meta"]["regularMarketPrice"])
        except (requests.RequestException, KeyError, IndexError, ValueError, TypeError) as error:
            logger.error("Ошибка получения цены %s: %s", stock, error)
            try:
                fallback = requests.get(
                    f"https://stooq.com/q/l/?s={stock.lower()}.us&f=sd2t2ohlcv&h&e=csv", timeout=5
                )
                fallback.raise_for_status()
                price = float(fallback.text.strip().split("\n")[1].split(",")[-1])
            except (requests.RequestException, ValueError, IndexError) as fallback_error:
                logger.error("Ошибка получения цены %s (Stooq): %s", stock, fallback_error)
        prices.append({"stock": stock, "price": price})
    return prices


def main_page(datetime_string: str, df: Optional[pd.DataFrame] = None) -> str:
    """Главная страница: принимает строку даты и возвращает JSON-ответ."""
    if df is None:
        df = read_transactions()
    dt = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")
    month_df = df[
        (df["Дата операции"] >= dt.replace(day=1))
        & (df["Дата операции"] <= dt)
    ]
    result = {
        "greeting": get_greeting(dt),
        "cards": get_cards(month_df),
        "top_transactions": get_top_transactions(month_df),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def get_date_range(dt: datetime, period: str = "M") -> tuple:
    """Возвращает начало и конец диапазона для периода W/M/Y/ALL."""
    if period == "W":
        start = dt - pd.Timedelta(days=dt.weekday())  # понедельник той же недели
        start = start.replace(hour=0, minute=0, second=0)
    elif period == "M":
        start = dt.replace(day=1, hour=0, minute=0, second=0)
    elif period == "Y":
        start = dt.replace(month=1, day=1, hour=0, minute=0, second=0)
    elif period == "ALL":
        start = pd.Timestamp.min
    else:
        raise ValueError(f"Неизвестный период: {period}")
    return start, dt


def get_expenses(df: pd.DataFrame) -> Dict[str, Any]:
    """Расходы: общая сумма, топ-7 категорий, «Остальное», переводы и наличные."""
    expenses = df[df["Сумма платежа"] < 0].copy()
    expenses["amount"] = expenses["Сумма платежа"].abs()

    main = (
        expenses.groupby("Категория")["amount"]
        .sum()
        .sort_values(ascending=False)
    )
    top = main.head(7)
    rest = round(float(main.iloc[7:].sum())) if len(main) > 7 else 0

    main_list = [{"category": cat, "amount": round(float(val))} for cat, val in top.items()]
    if rest > 0:
        main_list.append({"category": "Остальное", "amount": rest})

    cash = expenses[expenses["Категория"].isin(["Наличные", "Переводы"])]
    transfers = (
        cash.groupby("Категория")["amount"]
        .sum()
        .sort_values(ascending=False)
    )
    transfers_list = [
        {"category": cat, "amount": round(float(val))} for cat, val in transfers.items()
    ]

    return {
        "total_amount": round(float(expenses["amount"].sum())),
        "main": main_list,
        "transfers_and_cash": transfers_list,
    }


def get_income(df: pd.DataFrame) -> Dict[str, Any]:
    """Поступления: общая сумма и разбивка по категориям."""
    income = df[df["Сумма платежа"] > 0].copy()
    grouped = (
        income.groupby("Категория")["Сумма платежа"]
        .sum()
        .sort_values(ascending=False)
    )
    main_list = [{"category": cat, "amount": round(float(val))} for cat, val in grouped.items()]
    return {
        "total_amount": round(float(income["Сумма платежа"].sum())),
        "main": main_list,
    }


def events_page(datetime_string: str, period: str = "M", df: Optional[pd.DataFrame] = None) -> str:
    """Страница «События»: принимает дату и период, возвращает JSON-ответ."""
    if df is None:
        df = read_transactions()
    dt = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")
    start, end = get_date_range(dt, period)
    period_df = df[(df["Дата операции"] >= start) & (df["Дата операции"] <= end)]
    result = {
        "expenses": get_expenses(period_df),
        "income": get_income(period_df),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
    }
    return json.dumps(result, ensure_ascii=False, indent=2)
