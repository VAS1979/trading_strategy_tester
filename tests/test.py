""" . """

import csv
import logging
import json

FILEPATH = "dataframe_history/MTSS.csv"
FILEPATH_TO_FINISH_DATA = "processed_data/MTSS.csv"
FILEPATH_TO_JSON = "processed_data/MTSS.json"
INITIAL_CACHE = 400000
OPEN_PRICE = 215
CLOSE_PRICE = 300
COMISSION = 0.00035
TAX = 0.13
COLUMNS = ['date', 'high', 'low', 'cache', 'share_count', 'amount_in_shares',
           'overall_result']
input_data = [INITIAL_CACHE, OPEN_PRICE, CLOSE_PRICE, COMISSION, TAX]


def read_csv_with_header(fpath: str) -> list:
    """Считывает CSV файл построчно, оставляет
    столбцы с датой, максимальной и минимальной ценой
    и сохраняет в список `data_list`.

    Args:
        fpath: Путь к считываемому csv файлу.
        Считываемый csv файл имеет колонки:
            (open, close, high, low, value, volume, begin, end).

    Variables:
        data_list: Список для сохраняемых.
        closing_price: Цена закрытия дня.
        high_value: Максимальная цена.
        low_value: Минимальная цена за день.

    Returns:
        data_list: Список списков, каждый из которых описывает состояние
            торгового портфеля на определённую дату: [дата (str),
            максимальная цена (float), минимальная цена (float), цена закрытия
            дня (float)]. Возвращает None в случае ошибки.
    """

    try:
        data_list = []
        with open(fpath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    closing_price = float(row['close'].replace(',', '.'))
                    high_value = float(row['high'].replace(',', '.'))
                    low_value = float(row['low'].replace(',', '.'))
                    data_list.append([row['begin'], high_value, low_value,
                                      closing_price])
                except ValueError:
                    logging.error("Ошибка преобразования значения в число "
                                  "в строке: %s", row)
                except KeyError as e:
                    logging.error("Столбец %s не найден в строке: %s", e, row)
        return data_list

    except FileNotFoundError:
        logging.error("Файл %s не найден", fpath)
        return None
    except Exception as e:
        logging.error("Произошла общая ошибка: %s", e)
        return None


def calculates_data(data: list, in_data: list) -> list:
    """ Рассчитывает сценарий торговли на исторических данных

    Args:
        data: Список списков [дата, макс. цена, мин. цена, цена закрытия дня].
        in_data: Список [кэш, цена покупки, цена продажи, комиссия, налог].

    Variables:
        count: (float): Времененная величина для расчета количества акций.
        share_count (int): Количество приобретенных акций.
        amount_in_shares (float): Текущая стоимость всех приобретенных акций.
        overall_result (float): Текущий общий результат
            (стоимость акций + остаток кэша).
        in_data_copy (list): Копия списка in_data для работы с данными.

    Returns:
        data_list: Список списков, каждый из которых описывает состояние
            торгового портфеля на определённую дату: [дата (str),
            максимальная цена (float), минимальная цена (float), остаток
            кэша (float), количество акций (int), стоимость акций (float),
            общий результат (float)]. Возвращает None в случае ошибки.
    """

    try:
        share_count = 0
        amount_in_shares = 0
        overall_result = 0
        data_list = []

        in_data_copy = in_data.copy()
        cache = in_data_copy[0]
        open_price = in_data_copy[1]
        close_price = in_data_copy[2]

        for row in data:
            try:
                # если цена соответствует покупке:
                if row[2] <= open_price and cache >= row[2]:
                    count = cache // open_price
                    cache = cache - count * open_price
                    share_count += count
                # если цена соответствует продаже
                if row[1] >= close_price and share_count > 0:
                    cache = cache + share_count * row[1]
                    share_count = 0
                amount_in_shares = round(share_count * row[3], 2)
                overall_result = round(amount_in_shares + cache, 2)
                data_list.append([row[0], row[1], row[2], cache,
                                  share_count, amount_in_shares,
                                  overall_result])
            except KeyError as e:
                logging.error("Столбец %s не найден в строке: %s", e, row)
        return data_list

    except Exception as e:
        logging.error("Произошла общая ошибка: %s", e)
        return None


def calculates_results(data: list, in_data: list,
                       output_filepath: str) -> None:
    """ Рассчитывает финансовые результаты стратегии,
    выгружает в json

    Args:
        data: Список списков [дата, макс.цена, мин.цена, кэш, кол-во акций,
            стоимость акций, общий результат].
        output_filepath: Путь к создаваемому файлу.

    Variables:
        invest_period_day: Период инвестирования в днях.
        invest_period_years: Период инвестирования в годах.
        total_income_sum: Суммарный доход сумма.
        total_income_perc: Суммарный доход в процентах.
        incom_year_sum: Средний доход в год в сумме.
        incom_year_pers: Средний доход в год в процентах.

    """

    try:

        invest_period_days = len(data)
        invest_period_years = round(len(data) / 365, 1)

        total_income_sum = round((data[0][6] - data[-1][6]), 2) * -1
        total_income_perc = round(data[-1][6] / data[0][6] * 100, 2)

        incom_year_sum = total_income_sum / round(len(data) / 365, 1)
        incom_year_pers = round(total_income_perc / invest_period_years, 2)

        results = {
                "initial_cache": in_data[0],
                "open_price": in_data[1],
                "close_price": in_data[2],
                "comission_percent": in_data[3],
                "tax_percent": in_data[4],
                "invest_period_days": invest_period_days,
                "invest_period_years": invest_period_years,
                "total_income_sum": total_income_sum,
                "total_income_perc": total_income_perc,
                "incom_year_sum": incom_year_sum,
                "incom_year_pers": incom_year_pers,
            }

        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

    except (ValueError, TypeError, ZeroDivisionError) as e:
        raise ValueError("Ошибка при расчете или записи результатов: ") from e
    except IOError as e:
        raise IOError("Ошибка при работе с файлом: ") from e


def save_to_csv(data: list, columns: list, filename: str) -> None:
    """Сохраняет данные в CSV-файл.

    Args:
        data: Список списков: [дата, макс.цена, мин.цена, кэш, кол.акций
            стоимость акций, общий результат]
        columns: Список названий столбцов.
        filename: Имя сохраняемого файла
    """
    try:
        with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns)  # Записывает заголовок
            writer.writerows(data)     # Записывает данные
    except IOError as e:
        logging.error("Ошибка записи в файл %s: %s", filename, e)
        raise
    except Exception as e:
        logging.exception("Непредвиденная ошибка при сохранении "
                          "в файл %s: %s", filename, e)
        raise


df_list = read_csv_with_header(FILEPATH)
df_data = calculates_data(df_list, input_data)
save_to_csv(df_data, COLUMNS, FILEPATH_TO_FINISH_DATA)
calculates_results(df_data, input_data, FILEPATH_TO_JSON)
