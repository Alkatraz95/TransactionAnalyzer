## Структура проекта

```text
TransactionAnalyzer/
├── data/
│   └── operations.xlsx             # Исходная выгрузка банковских транзакций
├── reports/
│   ├── spending_by_category.json   # Сгенерированный отчет по категориям
│   └── spending_by_weekday.json    # Сгенерированный отчет по дням недели
├── src/
│   ├── __init__.py
│   ├── main.py                     # Точка входа (CLI-интерфейс на argparse)
│   ├── views.py                    # Логика генерации JSON для веб-страниц
│   ├── services.py                 # Поисковые и аналитические сервисы
│   ├── reports.py                  # Генерация отчетов с записью в файл
│   └── utils.py                    # Чтение Excel, работа с датами и внешними API
├── tests/
│   ├── test_main.py
│   ├── test_reports.py
│   ├── test_services.py
│   ├── test_utils.py
│   └── test_views.py
├── .env                            # API-ключи (исключен из Git)
├── requirements.txt                # Зависимости проекта
├── setup.cfg                       # Конфигурация линтеров и покрытия тестами
└── user_settings.json              # Пользовательские настройки валют и акций

## Установка и настройка

### 1. Клонирование репозитория

```bash
git clone https://github.com
cd TransactionAnalyzer


### 2. Создание виртуального окружения и установка зависимостей

```bash
python -m venv .venv

# Активация в Windows:
.venv\Scripts\activate

# Активация в Linux / macOS:
source .venv/bin/activate

# Установка зависимостей:
pip install -r requirements.txt

