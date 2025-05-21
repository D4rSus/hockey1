#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Главный модуль приложения "Рабочее место тренера хоккейной команды"
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale
from PyQt5.QtGui import QIcon, QFont

from config import Config
from database import init_db
from ui.auth import LoginWindow
from ui.main_window import MainWindow
from services.auth_service import AuthService

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
    """Основная функция приложения"""
    # Инициализация базы данных
    init_db()
    
    # Настройка приложения
    app = setup_app()
    
    # Инициализация сервиса авторизации
    auth_service = AuthService()
    
    # Создание окна авторизации
    login_window = LoginWindow(auth_service)
    
    # Обработка входа пользователя
    def on_login_success(user):
        """Обработчик успешной авторизации"""
        main_window = MainWindow(user)
        login_window.close()
        main_window.showMaximized()
    
    # Подключение сигнала успешной авторизации
    login_window.login_success.connect(on_login_success)
    
    # Отображение окна авторизации
    login_window.show()
    
    # Запуск цикла событий
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
