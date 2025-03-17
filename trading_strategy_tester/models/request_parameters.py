""" Содержит класс для хранения данных
    запроса парсеру """

from dataclasses import dataclass


@dataclass
class RequestParameters:
    """ Класс для хранения данных
    запроса парсеру """

    ticker: str
    start: str
    end: str
