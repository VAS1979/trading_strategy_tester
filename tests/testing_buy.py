""" Тестрование функционала покупки """
import logging


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

        in_data_copy = in_data.copy()
        cache = in_data_copy[0]
        open_price = in_data_copy[1]
        close_price = in_data_copy[2]
        comission = in_data_copy[3]
        # tax = in_data_copy[4]

        for row in data:
            try:
                # если цена соответствует покупке:
                if row[2] <= open_price and cache >= row[2]:
                    count = int(cache // open_price)
                    comiss_tmp = count * open_price * comission
                    # если сумма сделки + комиссия > кэша
                    print(f"предварительно - кэш: {cache}, цена для покупки: {open_price}, количество к покупке: {count}, сумма сделки: {open_price * count}, сумма сделки с учетом комиссии: {count * open_price + comiss_tmp}")
                    if cache < count * open_price + comiss_tmp:
                        count -= 1
                        
                        comiss_tmp = count * open_price * comission
                        print(f"факт         - кэш: {cache}, цена для покупки: {open_price}, количество к покупке: {count}, сумма сделки: {open_price * count}, сумма сделки с учетом комиссии: {count * open_price + comiss_tmp}")
                    comiss_sum += comiss_tmp
                    cache = cache - count * open_price - comiss_tmp
                    share_count += count
                    buy_count += 1
                # если цена соответствует продаже
                if row[1] >= close_price and share_count > 0:
                    comiss_tmp = share_count * row[1] * comission
                    cache = cache + share_count * row[1] - comiss_tmp
                    share_count = 0
                    sell_count += 1
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
        counting_transactions = [buy_count, sell_count]
        return data_list, counting_transactions

    except Exception as e:
        logging.error("Произошла общая ошибка: %s", e)
        return None


df_list = [['2014-12-15', 198.95, 171.05, 176.9]]
input_data = [400000, 215, 300, 0.00035, 0.13]

df_data = calculates_data(df_list, input_data)

print()
for i in df_data[0]:
    print(i, sep='\n')
