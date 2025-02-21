""" Модуль содержит константы, используемые в проекте """

import logging
from pathlib import Path

# Настройка логирования
log_dir = Path.cwd() / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

log_file = log_dir / "app.log"  # Полный путь к лог файлу
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(str(log_file), encoding='utf-8')
                    ])
