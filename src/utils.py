"""Модуль для чтения и подготовки данных о транзакциях из Excel-файла."""
import os
from typing import List, Dict, Any

import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT_DIR, "data", "operations.xlsx")


def read_transactions(file_path: str = DATA_FILE) -> pd.DataFrame:
    """Считывает Excel-файл и возвращает DataFrame с транзакциями."""
    df = pd.read_excel(file_path, engine="openpyxl")
    # Приводим колонку даты к datetime для дальнейшей фильтрации
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    return df


def get_transactions_list(file_path: str = DATA_FILE) -> List[Dict[str, Any]]:
    """Возвращает список словарей с транзакциями (для сервисов)."""
    df = read_transactions(file_path)
    return df.to_dict("records")
