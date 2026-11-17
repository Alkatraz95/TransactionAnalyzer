import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

import src.main as main_module


def test_build_parser_main_page():
    args = main_module.build_parser().parse_args(
        ["main_page", "--datetime", "2021-12-01 10:00:00"]
    )
    assert args.datetime == "2021-12-01 10:00:00"
    assert args.func is main_module.run_main_page


def test_build_parser_events_page_default_period():
    args = main_module.build_parser().parse_args(
        ["events_page", "--datetime", "2021-12-01 10:00:00"]
    )
    assert args.period == "M"


def test_build_parser_events_page_all_period():
    args = main_module.build_parser().parse_args(
        ["events_page", "--datetime", "2021-12-01 10:00:00", "--period", "ALL"]
    )
    assert args.period == "ALL"


def test_build_parser_cashback():
    args = main_module.build_parser().parse_args(
        ["cashback", "--year", "2021", "--month", "12"]
    )
    assert args.year == 2021
    assert args.month == 12
    assert args.func is main_module.run_cashback


def test_build_parser_investment_bank():
    args = main_module.build_parser().parse_args(
        ["investment_bank", "--month", "2021-12", "--limit", "50"]
    )
    assert args.limit == 50
    assert args.func is main_module.run_investment_bank


def test_build_parser_investment_bank_bad_limit():
    with pytest.raises(SystemExit):
        main_module.build_parser().parse_args(
            ["investment_bank", "--month", "2021-12", "--limit", "42"]
        )


def test_build_parser_search():
    args = main_module.build_parser().parse_args(["search", "--query", "колхоз"])
    assert args.query == "колхоз"
    assert args.func is main_module.run_search


def test_build_parser_phone():
    args = main_module.build_parser().parse_args(["phone"])
    assert args.func is main_module.run_phone


def test_build_parser_transfers_default_quarter():
    args = main_module.build_parser().parse_args(["transfers"])
    assert args.quarter == "Q1"


def test_build_parser_category_report():
    args = main_module.build_parser().parse_args(
        ["category_report", "--category", "Супермаркеты"]
    )
    assert args.category == "Супермаркеты"
    assert args.date is None
    assert args.func is main_module.run_category_report


def test_build_parser_weekday_report_with_date():
    args = main_module.build_parser().parse_args(
        ["weekday_report", "--date", "01.01.2022 00:00:00"]
    )
    assert args.date == "01.01.2022 00:00:00"
    assert args.func is main_module.run_weekday_report


def test_run_main_page(monkeypatch, capsys):
    called = {}

    def fake_main_page(datetime_string, df):
        called["datetime"] = datetime_string
        called["df"] = df
        return '{"greeting": "ok"}'

    monkeypatch.setattr(main_module, "read_transactions", lambda: "DATAFRAME")
    monkeypatch.setattr(main_module, "main_page", fake_main_page)
    args = main_module.build_parser().parse_args(
        ["main_page", "--datetime", "2021-12-01 10:00:00"]
    )
    main_module.run_main_page(args)
    out = capsys.readouterr().out
    assert called["df"] == "DATAFRAME"
    assert called["datetime"] == "2021-12-01 10:00:00"
    assert '{"greeting": "ok"}' in out


def test_run_events_page(monkeypatch, capsys):
    called = {}

    def fake_events_page(datetime_string, period, df):
        called["period"] = period
        return '{"events": "ok"}'

    monkeypatch.setattr(main_module, "read_transactions", lambda: "DATAFRAME")
    monkeypatch.setattr(main_module, "events_page", fake_events_page)
    args = main_module.build_parser().parse_args(
        ["events_page", "--datetime", "2021-12-01 10:00:00", "--period", "W"]
    )
    main_module.run_events_page(args)
    out = capsys.readouterr().out
    assert called["period"] == "W"
    assert '{"events": "ok"}' in out


def test_run_cashback(monkeypatch, capsys):
    called = {}

    def fake_cashback(df, year, month):
        called["year"] = year
        called["month"] = month
        return '{"cashback": "ok"}'

    monkeypatch.setattr(main_module, "read_transactions", lambda: "DATAFRAME")
    monkeypatch.setattr(main_module, "cashback_categories", fake_cashback)
    args = main_module.build_parser().parse_args(
        ["cashback", "--year", "2021", "--month", "12"]
    )
    main_module.run_cashback(args)
    out = capsys.readouterr().out
    assert called["year"] == 2021
    assert called["month"] == 12
    assert '{"cashback": "ok"}' in out


def test_run_investment_bank(monkeypatch, capsys):
    called = {}

    def fake_report(month, limit):
        called["month"] = month
        called["limit"] = limit
        return '{"saved": "ok"}'

    monkeypatch.setattr(main_module, "investment_bank_report", fake_report)
    args = main_module.build_parser().parse_args(
        ["investment_bank", "--month", "2021-12", "--limit", "10"]
    )
    main_module.run_investment_bank(args)
    out = capsys.readouterr().out
    assert called["month"] == "2021-12"
    assert called["limit"] == 10
    assert '{"saved": "ok"}' in out


def test_run_search(monkeypatch, capsys):
    monkeypatch.setattr(main_module, "read_transactions", lambda: "DATAFRAME")
    monkeypatch.setattr(main_module, "simple_search", lambda df, query: ["найдено"])
    args = main_module.build_parser().parse_args(["search", "--query", "колхоз"])
    main_module.run_search(args)
    assert "найдено" in capsys.readouterr().out


def test_run_phone(monkeypatch, capsys):
    monkeypatch.setattr(main_module, "read_transactions", lambda: "DATAFRAME")
    monkeypatch.setattr(main_module, "phone_number_search", lambda df: ["номер"])
    args = main_module.build_parser().parse_args(["phone"])
    main_module.run_phone(args)
    assert "номер" in capsys.readouterr().out


def test_run_transfers(monkeypatch, capsys):
    called = {}

    def fake_transfers(df, quarter):
        called["quarter"] = quarter
        return ["перевод"]

    monkeypatch.setattr(main_module, "read_transactions", lambda: "DATAFRAME")
    monkeypatch.setattr(main_module, "transfer_to_persons", fake_transfers)
    args = main_module.build_parser().parse_args(["transfers", "--quarter", "Q2"])
    main_module.run_transfers(args)
    out = capsys.readouterr().out
    assert called["quarter"] == "Q2"
    assert "перевод" in out


def test_run_category_report(monkeypatch, capsys):
    called = {}

    def fake_report(df, category, date):
        called["category"] = category
        called["date"] = date
        return '{"category": "ok"}'

    monkeypatch.setattr(main_module, "read_transactions", lambda: "DATAFRAME")
    monkeypatch.setattr(main_module, "spending_by_category", fake_report)
    args = main_module.build_parser().parse_args(
        ["category_report", "--category", "Супермаркеты"]
    )
    main_module.run_category_report(args)
    out = capsys.readouterr().out
    assert called["category"] == "Супермаркеты"
    assert called["date"] is None
    assert '{"category": "ok"}' in out


def test_run_weekday_report(monkeypatch, capsys):
    called = {}

    def fake_report(df, date):
        called["date"] = date
        return '{"weekday": "ok"}'

    monkeypatch.setattr(main_module, "read_transactions", lambda: "DATAFRAME")
    monkeypatch.setattr(main_module, "spending_by_weekday", fake_report)
    args = main_module.build_parser().parse_args(["weekday_report"])
    main_module.run_weekday_report(args)
    out = capsys.readouterr().out
    assert called["date"] is None
    assert '{"weekday": "ok"}' in out


def test_main_success(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["main", "phone"])
    monkeypatch.setattr(main_module, "read_transactions", lambda: "DATAFRAME")
    monkeypatch.setattr(main_module, "phone_number_search", lambda df: [])
    main_module.main()
    assert capsys.readouterr().out.strip() == "[]"


def test_main_error_prints_and_exits(monkeypatch, capsys):
    def boom(df):
        raise ValueError("сбой в сервисе")

    monkeypatch.setattr(sys, "argv", ["main", "phone"])
    monkeypatch.setattr(main_module, "read_transactions", lambda: "DATAFRAME")
    monkeypatch.setattr(main_module, "phone_number_search", boom)
    with pytest.raises(SystemExit) as exc:
        main_module.main()
    assert exc.value.code == 1
    assert "сбой в сервисе" in capsys.readouterr().err
