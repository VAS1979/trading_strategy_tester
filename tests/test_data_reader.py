""" Тестирование метода test_read_csv_with_header класса DataReader """

from trading_strategy_tester.models.trading_data import TradingData
from trading_strategy_tester.services.data_reader import DataReader


def test_read_csv_with_header(tmp_path, sample_csv_data):
    """
    Тестирует метод `read_csv_with_header` класса `DataReader`.
    Проверяет, что метод корректно считывает данные из CSV-файла
    и возвращает список объектов `TradingData`.

    Args:
        tmp_path: Временная директория для создания тестового файла.
        sample_trading_data: Фикстура с тестовыми данными.
    """

    # Создаем временный файл и записываем в него данные из фикстуры
    # с помощью фикстуры tmp_path из pytest, которая предоставляет
    # временную директорию для создания файлов.
    file_path = tmp_path / "test_data.csv"
    file_path.write_text(sample_csv_data)

    # Тестируем чтение данных
    data_reader = DataReader(filepath=str(file_path))
    data = data_reader.read_csv_with_header()

    # Проверяем результаты
    assert len(data) == 2
    assert isinstance(data[0], TradingData)
    assert data[0].date == "2014-01-06"
    assert data[0].high == 325.45
    assert data[0].low == 313.66
    assert data[0].close == 315.02


def test_read_csv_with_header_file_not_found():
    """
    Тестирует метод `read_csv_with_header` класса `DataReader` на случай,
    если файл не найден.
    Проверяет, что метод возвращает `None`, если файл отсутствует.
    """
    # Создаем объект DataReader с несуществующим файлом
    data_reader = DataReader(filepath="non_existent_file.csv")

    # Пытаемся прочитать данные
    data = data_reader.read_csv_with_header()

    # Проверяем, что данные не были загружены
    assert data is None
