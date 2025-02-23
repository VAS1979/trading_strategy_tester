""" . """

import csv
import logging
import json
from datetime import datetime

FILEPATH = "dataframe_history/MTSS.csv"
FILEPATH_TO_FINISH_DATA = "processed_data/MTSS.csv"
FILEPATH_TO_JSON = "processed_data/MTSS.json"
INITIAL_CACHE = 400000
OPEN_PRICE = 215
CLOSE_PRICE = 300
COMISSION = 0.00035
TAX = 0.13
COLUMNS = ['date', 'high', 'low', 'cache', 'share_count', 'amount_in_shares',
           'overall_result', 'comission', 'tax']
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
        overall_result (float): Общий результат (стоимость акций + кэш).
        buy_count (int): Количество покупок.
        sell_count (int): Количество продаж.
        in_data_copy (list): Копия списка in_data для работы с данными.

    Returns:
        data_list: Список списков, каждый из которых описывает состояние
            торгового портфеля на определённую дату: [дата, максимальная цена,
            минимальная цена, остаток кэша, количество акций, стоимость акций,
            общий результат].
        counting_transactions: Список сделок [кол-во покупок, кол-во продаж].
    """

    try:
        share_count = 0
        amount_in_shares = 0
        overall_result = 0
        buy_count = 0
        sell_count = 0
        comiss_sum = 0
        tax_sum = 0
        data_list = []
        buy_list = []
        sell_list = []

        in_data_copy = in_data.copy()
        cache = in_data_copy[0]
        open_price = in_data_copy[1]
        close_price = in_data_copy[2]
        comission = in_data_copy[3]
        # tax = in_data_copy[4]

        for row in data:
            try:
                # если цена соответствует покупке:
                if row[2] <= open_price and cache >= open_price:
                    count = int(cache // open_price)
                    comiss_tmp = count * open_price * comission
                    # если сумма сделки + комиссия > кэша
                    if cache < count * open_price + comiss_tmp:
                        count -= 1
                        comiss_tmp = count * open_price * comission
                    comiss_sum += comiss_tmp
                    cache = cache - count * open_price - comiss_tmp
                    share_count += count
                    buy_list.append(row[0])
                # если цена соответствует продаже
                if row[1] >= close_price and share_count > 0:
                    comiss_tmp = share_count * row[1] * comission
                    cache = cache + share_count * row[1] - comiss_tmp
                    share_count = 0
                    sell_list.append(row[0])
                    comiss_sum += comiss_tmp
                cache = round(cache, 2)
                comiss_sum = round(comiss_sum, 2)
                amount_in_shares = round(share_count * row[3], 2)
                overall_result = round(amount_in_shares + cache, 2)
                data_list.append([row[0], row[1], row[2], cache,
                                  share_count, amount_in_shares,
                                  overall_result, comiss_sum, tax_sum])
            except KeyError as e:
                logging.error("Столбец %s не найден в строке: %s", e, row)
        counting_transactions = [buy_list, sell_list]
        return data_list, counting_transactions

    except Exception as e:
        logging.error("Произошла общая ошибка: %s", e)
        return None


def calculates_results(data: list, transactions: list, in_data: list,
                       output_filepath: str) -> None:
    """ Рассчитывает финансовые результаты стратегии,
    выгружает в json

    Args:
        data: Список списков [дата, макс.цена, мин.цена, кэш, кол-во акций,
            стоимость акций, общий результат, комиссия по нарастающей,
            налог по нарастающей].
        transaction: Список сделок [список покупок, список продаж].
        in_data: Список задаваемых пользователем данных [стартовая сумма, цена
            для покупки, цена для продажи, процент комиссии брокера,
            процент налога].
        output_filepath: Путь к создаваемому файлу.

    Variables:
        start_date: Дата начала инвестирования.
        end_date: Дата завершения инвестрирования.
        invest_period_day: Период инвестирования в днях.
        invest_period_years: Период инвестирования в годах.
        total_income_sum: Суммарный доход сумма.
        total_income_perc: Суммарный доход в процентах.
        incom_year_sum: Средний доход в год в сумме.
        incom_year_pers: Средний доход в год в процентах.
        accumulated_commission: Накопленная сумма комиссии за весь период.
    """

    try:
        start_date = datetime.strptime(data[0][0], '%Y-%m-%d')
        end_date = datetime.strptime(data[-1][0], '%Y-%m-%d')

        invest_period_days = (end_date - start_date).days
        invest_period_years = round(invest_period_days / 365, 2)

        total_income_sum = round((data[0][6] - data[-1][6]), 2) * -1
        total_income_perc = round(data[-1][6] / data[0][6] * 100, 2)

        incom_year_sum = round(total_income_sum / invest_period_years, 2)
        incom_year_pers = round(total_income_perc / invest_period_years, 2)

        accumulated_commission = data[-1][7]

        results = {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "initial_cache": in_data[0],
                "open_price": in_data[1],
                "close_price": in_data[2],
                "comission_percent": in_data[3],
                "tax_percent": in_data[4],
                "buy_count": len(transactions[0]),
                "purchase_dates": transactions[0],
                "sell_count": len(transactions[1]),
                "sales_dates": transactions[1],
                "invest_period_days": invest_period_days,
                "invest_period_years": invest_period_years,
                "total_income_sum": total_income_sum,
                "total_income_perc": total_income_perc,
                "incom_year_sum": incom_year_sum,
                "incom_year_pers": incom_year_pers,
                "accumulated_commission": accumulated_commission
            }

        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

    except (ValueError, TypeError, ZeroDivisionError) as e:
        logging.exception("Ошибка при расчете или записи результатов: %s", e)
        raise
    except IOError as e:
        logging.exception("Ошибка при работе с файлом: %s", e)
        raise


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
save_to_csv(df_data[0], COLUMNS, FILEPATH_TO_FINISH_DATA)
calculates_results(df_data[0], df_data[1], input_data, FILEPATH_TO_JSON)
