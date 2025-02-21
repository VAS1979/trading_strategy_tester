""" Парсит инфу по акции на исторических данных """

from moexalgo import Ticker

from trading_strategy_tester.config import logging

# Константа тикера
TICKER = 'MTSS'

# Началная дата расчетов вида гггг-мм-дд
START = '2014-01-01'

# Конечная дата расчетов вида гггг-мм-дд
END = '2024-12-28'

# Путь к директории сохранения ценовой истории с названием файла 
DIR = f"dataframe_history/{TICKER}.csv"

# Обьект класса Ticker
ticker = Ticker(TICKER)

# Свечи по акции за период
df = ticker.candles(start=START, end=END, period='1d')
print(df)


def parses_dataframe():
    """ Парсит ценовую историю и сохраняет
    датафрейм в csv файл """

    # Определяет желаемый порядок столбцов.
    desired_columns = ['open', 'close', 'high', 'low', 'value',
                       'volume', 'begin', 'end']
    # Проверяет, существуют ли все столбцы в DataFrame
    missing_cols = set(desired_columns) - set(df.columns)
    if missing_cols:
        logging.error("Ошибка: Столбцы %s отсутствуют в DataFrame",
                      missing_cols)
    else:
        # Сохраняет в CSV-файл с указанным порядком столбцов:
        df.to_csv(DIR, columns=desired_columns, index=False)
        logging.info("Данные успешно сохранены в %s", DIR)
