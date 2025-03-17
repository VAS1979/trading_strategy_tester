##### Описание проекта
Приложение предназначено для анализа торговой стратегии на историческом промежутке, на основании введенных начальных данных.


##### Функционал проекта
На этапе разработи:
facade.parsing_facade -запрос и сохранение датафрейма с историческими данными.
facade.project_facade.py -запуск торговой стратегии.
Позже интерфейс по работе программы будет осуществлен с использованием FastAPI.


##### Структура проекта
trading_strategy_tester/
├── trading_strategy_tester/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── routers.py
│   │   └── schemas.py
│   ├── facade/
│   │   ├── __init__.py
|   |   ├── parsing_facade.py
│   │   └── project_facade.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request_parameters.py
│   │   ├── strategy_parameters.py
|   |   ├── trading_data.py
|   |   └── trading_result.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── calculate_results.py
│   │   ├── data_parser.py
│   │   ├── data_reader.py
|   |   ├── result_saver.py
│   │   └── strategy_calculator.py
│   ├── templates/
│   │   └── index.html
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_data_reader.py
│   ├── test_strategy_calculator.py
│   ├── test_result_saver.py
│   ├── test_trading_strategy_facade.py
│   └── test_data_parser.py
├── database/
│   ├── dataframe_history/
|   └── processed_data/
├── logs/
│   └── app.log
├── pyproject.lock
├── pyproject.toml
├── README.md
└── .gitignore


##### Трэкер
+ Зедача завершена.
. Задача в работе
  Задача запланирована.

+ Структура проекта
+ Модуль логирования работы приложения utils/logger.py
+ Чтение CSV-файла, сформированного парсером.
   + services.data_reader
   + models.trading_data
   + tests.test_data_reader.py
   + tests.conftest.py
Бизнес-логика (рассчет доходности на основе сценария)
   + services.strategy_calculator.py
   + services.calculate_results.py
   + models.strategy_parameters.py
   + models.trading_result.py
   tests.test_strategy_calculator.py
   tests.conftest.py
Сохранение результатов
   + services.result_saver.py
Обработка цепочки вызовов
   . facade.project_facade.py ? ___После подключения api убрать вызов функции в модуле
Запрос парсером датафрэйма
   + services.data_parser.py
   + models.request_parameters.py
   + services.result_saver.py
   . facade.parsing_facade ? ___После подключения api убрать вызов функции в модуле
Создание api на FastAPI
   + Модуль точки входа в приложение api/app.py
   . Модуль с роутерами api/routers.py ? ___доработать функционал
   . Шаблон html страницы templates/index.html ? ___доработать функционал



Снятие налога происходит в конце года, как на обычном брокерском счете
