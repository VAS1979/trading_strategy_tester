""" . """

import csv
import logging
import json
from datetime import datetime

FILEPATH = "dataframe_history/MTSS.csv"  # Путь к свечному датафрэйму
FILEPATH_TO_FINISH_DATA = "processed_data/MTSS.csv"  # Сформированный отчет
FILEPATH_TO_JSON = "processed_data/MTSS.json"  # JSON сводные данные
INITIAL_CACHE = 400000  # Начальная сумма кэша
BUY_PRICE = 215  # Цена покупки по условию
CLOSE_PRICE = 300  # Цена продажи по условию
COMISSION = 0.00035  # Ставка комиссии брокера
TAX = 0.13  # Налоговая ставка
# Наименование колонок итогового CSV отчета
COLUMNS = ['date', 'high', 'low', 'cache', 'share_count', 'amount_in_shares',
           'overall_result', 'comission', 'tax', 'total_tax']
# Список вводных данных для расчетов
input_data = [INITIAL_CACHE, BUY_PRICE, CLOSE_PRICE, COMISSION, TAX]


def read_csv_with_header(fpath: str) -> list:
    """Считывает CSV файл со свечным датафреймом построчно, оставляет
    столбцы с датой, максимальной и минимальной ценой и сохраняет
    в список `data_list`.

    Args:
        fpath: Путь к считываемому csv файлу.
        Считываемый csv файл имеет колонки:
            (open, close, high, low, value, volume, begin, end).

    Variables:
        data_list: Список для сохраняемых.
        closing_price: Цена закрытия дня.
        high_value: Максимальная цена за день.
        low_value: Минимальная цена за день.

    Returns:
        data_list: Список списков, каждый из которых описывает состояние
            торгового портфеля на определённую дату: [дата (str),
            максимальная цена (float), минимальная цена (float), цена закрытия
            дня (float)].
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
                except ValueError as e:
                    logging.error("Ошибка преобразования значения в число "
                                  "в строке %s, ошибка: %s", row, e)
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
    """ Рассчитывает сценарий торговли на исторических данных.

    Args:
        data: Список списков, каждый из которых описывает состояние
            торгового портфеля на определённую дату
            [дата, макс. цена, мин. цена, цена закрытия дня].
        in_data: Список [кэш, цена покупки, цена продажи, комиссия, налог].

    Variables:
        share_count (int): Количество приобретенных акций.
        amount_in_shares (float): Текущая стоимость всех приобретенных акций.
        overall_result (float): Общий результат (стоимость акций + кэш).
        buy_count (int): Количество покупок.
        sell_count (int): Количество продаж.
        comiss_sum (float): Сумма комиссии по нарастающей.
        tax_sum (float): Сумма налога за текущий год по нарастающей.
        total_tax (float): Общая сумма налога за весь период по нарастающей.
        years_list (list): Сюда вносится год, после вычета налога, в конце
            года, для исключения повторного списания.
        count: (float): Времененная величина для расчета количества акций.
        date_str (str): Дата.

    Returns:
        data_list: Список списков, каждый из которых описывает состояние
            торгового портфеля на определённую дату: [date_str, max_price,
            min_price, cache, share_count, amount_in_shares, overall_result,
            comiss_sum, tax_sum, total_tax].
        counting_transactions: Список сделок [buy_count, sell_count].
    """

    try:
        share_count = 0
        amount_in_shares = 0
        overall_result = 0
        buy_count = 0
        sell_count = 0
        comiss_sum = 0
        tax_sum = 0
        total_tax = 0
        data_list = []
        years_list = []

        cache, buy_price, sell_price, commission_rate, tax_rate = in_data
        price_differ = sell_price - buy_price

        for row in data:
            date_str, max_price, min_price, closing_price = row
            current_date = datetime.strptime(date_str, '%Y-%m-%d')

            try:
                # Логика обработки покупок
                if cache >= buy_price >= min_price:
                    count = int(cache // buy_price)
                    comiss_tmp = count * buy_price * commission_rate
                    # Если сумма сделки + комиссия > кэша
                    if cache < count * buy_price + comiss_tmp:
                        while count * buy_price + comiss_tmp > cache:
                            count -= 1
                        comiss_tmp = count * buy_price * commission_rate
                    comiss_sum += comiss_tmp
                    cache = cache - count * buy_price - comiss_tmp
                    share_count += count
                    buy_count += 1

                # Логика обработки продаж
                tax_tmp = 0

                if max_price >= sell_price and share_count > 0:
                    comiss_tmp = share_count * sell_price * commission_rate
                    cache = cache + share_count * sell_price - comiss_tmp
                    tax_tmp = round(price_differ * share_count * tax_rate, 2)
                    share_count = 0
                    sell_count += 1
                    comiss_sum += comiss_tmp

                # Завершающая обработка
                amount_in_shares = share_count * closing_price
                overall_result = amount_in_shares + cache
                tax_sum = tax_sum + tax_tmp
                total_tax += tax_tmp

                # Снятие налога в конце года
                year = current_date.year
                month = current_date.month
                day = current_date.day
                if year not in years_list and month == 12 and 20 <= day <= 31:
                    years_list.append(year)
                    cache -= tax_sum
                    tax_sum = 0

                # Округление результатов
                cache = round(cache, 2)
                comiss_sum = round(comiss_sum, 2)
                amount_in_shares = round(amount_in_shares, 2)
                overall_result = round(overall_result, 2)
                total_tax = round(total_tax, 2)

                data_list.append([date_str, max_price, min_price, cache,
                                  share_count, amount_in_shares,
                                  overall_result, comiss_sum, tax_sum,
                                  total_tax])

            except KeyError as e:
                logging.error("Столбец %s не найден в строке: %s", e, row)

        # Вычет налога в конце срока, если он не в конце декабря
        data_list[-1][3] -= data_list[-1][8]
        data_list[-1][8] = 0

        counting_transactions = [buy_count, sell_count]
        return data_list, counting_transactions

    except Exception as e:
        logging.error("Произошла общая ошибка: %s", e)
        return None


def calculates_results(data: list, transactions: list, in_data: list,
                       output_filepath: str) -> None:
    """ Рассчитывает итоговые финансовые результаты стратегии,
    выгружает в json.

    Args:
        data: Список списков [дата, макс.цена, мин.цена, кэш, кол-во акций,
            стоимость акций, общий результат, комиссия по нарастающей,
            налог за год по нарастающей, сумма налога за весь период].
        transaction: Список сделок [кол-во покупок, кол-во продаж].
        in_data: Список задаваемых пользователем данных [стартовая сумма, цена
            для покупки, цена для продажи, процент комиссии брокера,
            процент налога].
        output_filepath: Путь к создаваемому файлу.

    Variables:
        start_date: Дата начала инвестирования.
        end_date: Дата завершения инвестрирования.
        initial_cache: Начальная сумма кэша.
        buy_price: Цена покупки по условию стратегии.
        sell_price: Цена продажи по условию стратегии.
        buy_count: Количество сделок покупки.
        sell_count: Количество сделок продаж.
        comission_percent: Процентная ставка комиссии брокера.
        tax_percent: Процентная ставка налога.
        invest_period_day: Период инвестирования в днях.
        invest_period_years: Период инвестирования в годах.
        total_income_sum: Суммарный доход сумма.
        total_income_perc: Суммарный доход в процентах.
        incom_year_sum: Средний доход в год в сумме.
        incom_year_pers: Средний доход в год в процентах.
        accumulated_commission: Сумма комиссии за весь период.
        final_cache: Итоговая сумма в кэше.
        final_amount_in_shares: Итоговая сумма в акциях.
        final_overall_result: Общая итоговая сумма.
        total_tax: Общая сумма налога за весь период.
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
        total_tax = data[-1][9]
        final_cache = data[-1][3]
        final_amount_in_shares = data[-1][5]
        final_overall_result = data[-1][6]

        results = {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "initial_cache": in_data[0],
                "buy_price": in_data[1],
                "sell_price": in_data[2],
                "buy_count": transactions[0],
                "sell_count": transactions[1],
                "comission_percent": in_data[3],
                "tax_percent": in_data[4],
                "invest_period_days": invest_period_days,
                "invest_period_years": invest_period_years,
                "total_income_sum": total_income_sum,
                "total_income_perc": total_income_perc,
                "incom_year_sum": incom_year_sum,
                "incom_year_pers": incom_year_pers,
                "accumulated_commission": accumulated_commission,
                "final_cache": final_cache,
                "final_amount_in_shares": final_amount_in_shares,
                "final_overall_result": final_overall_result,
                "total_tax": total_tax
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
        data: Список списков: [дата, макс.цена, мин.цена, кэш, кол-во акций,
            стоимость акций, общий результат, комиссия по нарастающей,
            налог за год по нарастающей, общая сумма налога за весь период]
        columns: Список названий столбцов.
        filename: Имя и путь сохраняемого файла.
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
