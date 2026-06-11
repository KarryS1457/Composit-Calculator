import logging
from logging.handlers import RotatingFileHandler
import os
import sys

def setup_logger():
    if getattr(sys, 'frozen', False):
        # В собранной программе логи пишем в профиль пользователя,
        # чтобы рядом с exe не появлялось никаких файлов
        base_dir = os.path.join(
            os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".config"),
            "CompositCalculator")
    else:
        # Если запущено как python-скрипт
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    log_dir = os.path.join(base_dir, "logs")
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, 'app.log')

    # Создаем логгер
    logger = logging.getLogger('CalcApp')
    logger.setLevel(logging.DEBUG) # Логируем всё: от DEBUG до CRITICAL

    # Формат сообщений: Дата Время - Уровень - [Файл:Строка] - Сообщение
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s', 
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # 1. Файловый обработчик с ротацией (максимум 5 МБ на файл, храним 3 старых файла)
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # 2. Консольный обработчик (чтобы видеть логи в PyCharm/терминале при разработке)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # Добавляем обработчики к логгеру
    # Проверка, чтобы не добавлять обработчики дважды при горячей перезагрузке
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Создаем глобальный объект логгера, который будем импортировать в другие файлы
log = setup_logger()