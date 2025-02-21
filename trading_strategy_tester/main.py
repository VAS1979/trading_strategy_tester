""" Модуль для запуска проекта """

from trading_strategy_tester.config import logging
from trading_strategy_tester.stock_quotes.parser import (
    parses_dataframe)


def main() -> None:
    """ Запуск проекта """

    try:
        print("1 -запросить датафрэйм\n2 -запустить анализатор")
        action = int(input("Введите число 1 или 2"))
        if action == 1:
            parses_dataframe()
            logging.info("Успешное выполнение")
        elif action == 2:
            
    except Exception as e:
        logging.error("Ошибка, модуль main(): %s", e)


if __name__ == "__main__":
    main()
