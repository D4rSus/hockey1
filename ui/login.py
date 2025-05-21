#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QMessageBox, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont

from ui.main_window import MainWindow
from database import authenticate_user

class LoginWindow(QDialog):
    """
    Окно авторизации пользователя
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle('Авторизация - Система тренера хоккейной команды')
        self.setFixedSize(400, 300)
        
        # Создаем основной layout
        main_layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel('Автоматизированное рабочее место тренера хоккейной команды')
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Форма авторизации
        form_layout = QFormLayout()
        
        # Поле для имени пользователя
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Введите имя пользователя')
        form_layout.addRow('Пользователь:', self.username_input)
        
        # Поле для пароля
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Введите пароль')
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow('Пароль:', self.password_input)
        
        # Добавляем форму на основной layout
        main_layout.addLayout(form_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        # Кнопка входа
        self.login_button = QPushButton('Войти')
        self.login_button.clicked.connect(self.login)
        button_layout.addWidget(self.login_button)
        
        # Кнопка отмены
        self.cancel_button = QPushButton('Отмена')
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)
        
        # Добавляем кнопки на основной layout
        main_layout.addLayout(button_layout)
        
        # Информация
        info_label = QLabel('По умолчанию: admin / admin123')
        info_label.setAlignment(Qt.AlignCenter)
        info_font = QFont()
        info_font.setItalic(True)
        info_font.setPointSize(8)
        info_label.setFont(info_font)
        main_layout.addWidget(info_label)
        
        # Устанавливаем layout для окна
        self.setLayout(main_layout)
        
        # Enter для отправки формы
        self.username_input.returnPressed.connect(self.login)
        self.password_input.returnPressed.connect(self.login)
        
        # Фокус на поле имени пользователя при запуске
        self.username_input.setFocus()
    
    def login(self):
        """Обработка входа пользователя"""
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Ошибка', 'Введите имя пользователя и пароль')
            return
            
        user = authenticate_user(username, password)
        
        if user:
            self.accept()
            self.main_window = MainWindow(user)
            self.main_window.show()
        else:
            QMessageBox.warning(self, 'Ошибка аутентификации', 
                               'Неверное имя пользователя или пароль')
            self.password_input.clear()
            self.password_input.setFocus()
