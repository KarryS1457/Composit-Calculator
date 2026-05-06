from model import AppModel
from view import MainView
from presenter import AppPresenter

def main():
    # 1. Создаем Модель (Хранилище логики и системных данных)
    model = AppModel()

    # 2. Создаем Вид (Оболочка окна)
    view = MainView()

    # 3. Создаем Презентер (Мозг, который связывает Model и View)
    presenter = AppPresenter(model, view)

    # 4. Запускаем приложение через Презентер
    presenter.start()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Критическая ошибка при запуске: {e}")
        input("Нажмите Enter, чтобы выйти...")