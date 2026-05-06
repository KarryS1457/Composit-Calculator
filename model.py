import os
import sys

class AppModel:
    def __init__(self):
        # Настройки приложения
        self.secret_code = "chuu"
        self.app_title = "Калькулятор Composit v4"

    def get_resource_path(self, relative_path):
        """Определяет путь к файлам (картинкам, иконкам) для сборки в .exe"""
        try:
            # Путь для PyInstaller
            base_path = sys._MEIPASS
        except Exception:
            # Путь при обычной разработке
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)

    def check_secret(self, typed_buffer):
        """Проверяет, совпал ли введенный код с секретным"""
        return typed_buffer == self.secret_code

    def validate_numeric(self, P):
        """Логика валидации ввода (используется в Entry).
        Разрешает только положительные числа, не длиннее 8 символов."""
        if P == "": 
            return True
        try:
            # Проверяем, что это число и оно не отрицательное
            if float(P) >= 0 and len(P) <= 8 and "+" not in P and "-" not in P:
                return True
            return False
        except ValueError:
            return False

    def get_image_data(self, path):
        """Проверяет наличие картинки и возвращает абсолютный путь"""
        abs_path = self.get_resource_path(path)
        if os.path.exists(abs_path):
            return abs_path
        return None
