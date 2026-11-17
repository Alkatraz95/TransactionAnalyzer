import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils import read_transactions, get_transactions_list


def test_read_transactions_not_empty():
    df = read_transactions()
    assert not df.empty


def test_read_transactions_has_required_columns():
    df = read_transactions()
    for column in ["Дата операции", "Сумма операции", "Категория", "Описание"]:
        assert column in df.columns


def test_date_column_is_datetime():
    df = read_transactions()
    assert str(df["Дата операции"].dtype).startswith("datetime64")


def test_get_transactions_list_returns_list_of_dicts():
    result = get_transactions_list()
    assert isinstance(result, list)
    assert isinstance(result[0], dict)
