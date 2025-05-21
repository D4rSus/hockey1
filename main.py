import sys
import os

from ui.team_roster import TeamRosterWidget
# Указываем Qt использовать Offscreen платформу для работы в среде Replit
os.environ["QT_QPA_PLATFORM"] = "windows"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale
from PyQt5.QtGui import QIcon, QFont

from config import Config
from database import init_db
from ui.auth import LoginWindow
from ui.main_window import MainWindow
from services.auth_service import AuthService



def init_ui(self):
    self.setup_main_widgets()  # Сначала создаем все виджеты
    self.create_menu()        # Затем создаем меню
    self.setup_layout()       # Настраиваем компоновку

def setup_main_widgets(self):
    """Инициализация всех виджетов главного окна"""
    self.team_roster_widget = TeamRosterWidget(self.user)

def setup_app():
    """Настройка приложения"""
    # Создаем приложение
    app = QApplication(sys.argv)

    # Устанавливаем имя приложения
    app.setApplicationName("Рабочее место тренера хоккейной команды")

    # Загрузка стилей
    with open("resources/styles.qss", "r", encoding="utf-8") as file:
        app.setStyleSheet(file.read())

    # Настройка шрифтов
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    return app

def main():
    app = QApplication(sys.argv)

    # Инициализация
    init_db()
    auth_service = AuthService()
    login_window = LoginWindow(auth_service)

    # Храним ссылку на главное окно
    main_window = None

    def on_login_success(user):
        nonlocal main_window
        try:
            main_window = MainWindow(user)
            login_window.close()
            main_window.show()
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Ошибка: {str(e)}")
            sys.exit(1)

    login_window.login_success.connect(on_login_success)
    login_window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
