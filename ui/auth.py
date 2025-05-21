# -*- coding: utf-8 -*-

"""
Модуль для авторизации пользователя
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QPushButton, QMessageBox,
                           QFormLayout, QGroupBox)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QIcon, QFont

from services.auth_service import AuthService
from utils import show_error_message

class LoginWindow(QMainWindow):
    """Окно авторизации"""
    
    # Сигнал об успешной авторизации
    login_success = pyqtSignal(object)
    
    def __init__(self, auth_service):
        super().__init__()
        
        self.auth_service = auth_service
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        # Настройка окна
        self.setWindowTitle("Авторизация - Рабочее место тренера хоккейной команды")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title_label = QLabel("Рабочее место тренера\nхоккейной команды")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Группа полей авторизации
        login_group = QGroupBox("Вход в систему")
        login_layout = QFormLayout()
        
        # Поле имени пользователя
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Введите имя пользователя")
        login_layout.addRow(QLabel("Имя пользователя:"), self.username_edit)
        
        # Поле пароля
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Введите пароль")
        login_layout.addRow(QLabel("Пароль:"), self.password_edit)
        
        login_group.setLayout(login_layout)
        main_layout.addWidget(login_group)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        
        # Кнопка входа
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login)
        buttons_layout.addWidget(self.login_button)
        
        # Кнопка выхода
        exit_button = QPushButton("Выход")
        exit_button.clicked.connect(self.close)
        buttons_layout.addWidget(exit_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Фокус на поле имени пользователя
        self.username_edit.setFocus()
        
        # Подключение события Enter
        self.username_edit.returnPressed.connect(self.password_edit.setFocus)
        self.password_edit.returnPressed.connect(self.login)
    
    def login(self):
        """Обработка входа в систему"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        # Проверка заполненности полей
        if not username or not password:
            show_error_message(self, "Ошибка", "Необходимо заполнить все поля")
            return
        
        # Попытка авторизации
        user = self.auth_service.authenticate(username, password)
        
        if user:
            # Авторизация успешна
            self.login_success.emit(user)
        else:
            # Ошибка авторизации
            show_error_message(self, "Ошибка аутентификации", "Неверное имя пользователя или пароль")
            self.password_edit.clear()
            self.password_edit.setFocus()
