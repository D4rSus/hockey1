# -*- coding: utf-8 -*-

"""
Виджет для отображения карточки игрока
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, 
                           QLabel, QTabWidget, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QGroupBox, QFormLayout, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

from models import Player, PlayerStats
from services.player_service import PlayerService
from services.stats_service import StatsService
from utils import format_date, show_error_message, show_info_message, get_player_photo_path, generate_chart

class PlayerCardWidget(QWidget):
    """Виджет для отображения карточки игрока"""
    
    def __init__(self):
        super().__init__()
        
        self.player = None
        self.player_service = PlayerService()
        self.stats_service = StatsService()
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        
        # Верхняя панель с информацией об игроке
        top_panel = QHBoxLayout()
        
        # Фото игрока
        self.photo_widget = QWidget()
        photo_layout = QVBoxLayout(self.photo_widget)
        
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(200, 200)
        self.photo_label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
        self.photo_label.setAlignment(Qt.AlignCenter)
        photo_layout.addWidget(self.photo_label)
        
        self.change_photo_button = QPushButton("Изменить фото")
        self.change_photo_button.clicked.connect(self.change_photo)
        photo_layout.addWidget(self.change_photo_button)
        
        top_panel.addWidget(self.photo_widget)
        
        # Основная информация
        info_group = QGroupBox("Основная информация")
        info_layout = QFormLayout(info_group)
        
        self.player_name_label = QLabel()
        self.player_name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        info_layout.addRow("ФИО:", self.player_name_label)
        
        self.birth_date_label = QLabel()
        info_layout.addRow("Дата рождения:", self.birth_date_label)
        
        self.age_label = QLabel()
        info_layout.addRow("Возраст:", self.age_label)
        
        self.position_label = QLabel()
        info_layout.addRow("Амплуа:", self.position_label)
        
        self.team_label = QLabel()
        info_layout.addRow("Команда:", self.team_label)
        
        self.jersey_number_label = QLabel()
        info_layout.addRow("Номер:", self.jersey_number_label)
        
        self.height_label = QLabel()
        info_layout.addRow("Рост:", self.height_label)
        
        self.weight_label = QLabel()
        info_layout.addRow("Вес:", self.weight_label)
        
        top_panel.addWidget(info_group, 1)
        
        # Статистика сезона
        season_stats_group = QGroupBox("Статистика сезона")
        stats_layout = QFormLayout(season_stats_group)
        
        self.games_label = QLabel()
        stats_layout.addRow("Игр:", self.games_label)
        
        self.goals_label = QLabel()
        stats_layout.addRow("Голы:", self.goals_label)
        
        self.assists_label = QLabel()
        stats_layout.addRow("Передачи:", self.assists_label)
        
        self.points_label = QLabel()
        stats_layout.addRow("Очки (Г+П):", self.points_label)
        
        self.penalty_minutes_label = QLabel()
        stats_layout.addRow("Штраф. мин.:", self.penalty_minutes_label)
        
        self.plus_minus_label = QLabel()
        stats_layout.addRow("+/-:", self.plus_minus_label)
        
        top_panel.addWidget(season_stats_group, 1)
        
        layout.addLayout(top_panel)
        
        # Вкладки с детальной информацией
        self.tabs = QTabWidget()
        
        # Вкладка со статистикой по матчам
        self.stats_tab = QWidget()
        stats_layout = QVBoxLayout(self.stats_tab)
        
        self.stats_table = QTableWidget()
        self.stats_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.stats_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.stats_table.setColumnCount(9)
        self.stats_table.setHorizontalHeaderLabels([
            "Дата", "Матч", "Голы", "Передачи", "Очки", "+/-", "Штраф. мин.", "Броски", "Время на льду"
        ])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        stats_layout.addWidget(self.stats_table)
        
        # Кнопки действий
        buttons_layout = QHBoxLayout()
        
        chart_button = QPushButton("Графики")
        chart_button.clicked.connect(self.show_charts)
        buttons_layout.addWidget(chart_button)
        
        buttons_layout.addStretch()
        
        add_stats_button = QPushButton("Добавить статистику")
        add_stats_button.clicked.connect(self.add_stats)
        buttons_layout.addWidget(add_stats_button)
        
        edit_stats_button = QPushButton("Редактировать")
        edit_stats_button.clicked.connect(self.edit_stats)
        buttons_layout.addWidget(edit_stats_button)
        
        export_button = QPushButton("Экспорт")
        export_button.clicked.connect(self.export_stats)
        buttons_layout.addWidget(export_button)
        
        stats_layout.addLayout(buttons_layout)
        
        self.tabs.addTab(self.stats_tab, "Статистика по матчам")
        
        # Вкладка с видео
        self.video_tab = QWidget()
        video_layout = QVBoxLayout(self.video_tab)
        
        self.video_table = QTableWidget()
        self.video_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.video_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.video_table.setColumnCount(4)
        self.video_table.setHorizontalHeaderLabels([
            "Название", "Дата", "Тип", "Описание"
        ])
        self.video_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        video_layout.addWidget(self.video_table)
        
        video_buttons_layout = QHBoxLayout()
        
        add_video_button = QPushButton("Добавить видео")
        add_video_button.clicked.connect(self.add_video)
        video_buttons_layout.addWidget(add_video_button)
        
        play_video_button = QPushButton("Просмотр")
        play_video_button.clicked.connect(self.play_video)
        video_buttons_layout.addWidget(play_video_button)
        
        delete_video_button = QPushButton("Удалить")
        delete_video_button.clicked.connect(self.delete_video)
        video_buttons_layout.addWidget(delete_video_button)
        
        video_layout.addLayout(video_buttons_layout)
        
        self.tabs.addTab(self.video_tab, "Видеоматериалы")
        
        # Вкладка с заметками
        self.notes_tab = QWidget()
        notes_layout = QVBoxLayout(self.notes_tab)
        self.notes_label = QLabel("Выберите игрока для просмотра заметок")
        notes_layout.addWidget(self.notes_label)
        
        self.tabs.addTab(self.notes_tab, "Заметки")
        
        layout.addWidget(self.tabs)
        
        # Установка сообщения по умолчанию
        self.set_default_message()
    
    def set_default_message(self):
        """Установка сообщения по умолчанию"""
        self.player_name_label.setText("Выберите игрока")
        self.birth_date_label.setText("")
        self.age_label.setText("")
        self.position_label.setText("")
        self.team_label.setText("")
        self.jersey_number_label.setText("")
        self.height_label.setText("")
        self.weight_label.setText("")
        
        self.games_label.setText("")
        self.goals_label.setText("")
        self.assists_label.setText("")
        self.points_label.setText("")
        self.penalty_minutes_label.setText("")
        self.plus_minus_label.setText("")
        
        self.photo_label.setText("Нет фото")
        self.photo_label.setPixmap(QPixmap())
        
        self.stats_table.setRowCount(0)
        self.video_table.setRowCount(0)
        self.notes_label.setText("Выберите игрока для просмотра заметок")
    
    def load_player(self, player):
        """Загрузка информации об игроке"""
        if not player:
            self.set_default_message()
            return
        
        self.player = player
        
        # Основная информация
        self.player_name_label.setText(player.full_name)
        self.birth_date_label.setText(format_date(player.birth_date) if player.birth_date else "Не указана")
        self.age_label.setText(str(player.age) if player.age else "Неизвестно")
        self.position_label.setText(player.position)
        self.team_label.setText(player.team.name if player.team else "Не указана")
        self.jersey_number_label.setText(str(player.jersey_number) if player.jersey_number else "Нет")
        self.height_label.setText(f"{player.height} см" if player.height else "Не указан")
        self.weight_label.setText(f"{player.weight} кг" if player.weight else "Не указан")
        
        # Загрузка фото
        if player.photo_path:
            pixmap = QPixmap(player.photo_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.photo_label.setPixmap(pixmap)
                self.photo_label.setText("")
            else:
                self.photo_label.setText("Ошибка загрузки фото")
                self.photo_label.setPixmap(QPixmap())
        else:
            self.photo_label.setText("Нет фото")
            self.photo_label.setPixmap(QPixmap())
        
        # Загрузка статистики сезона
        self.load_season_stats()
        
        # Загрузка статистики по матчам
        self.load_match_stats()
        
        # Загрузка видеоматериалов
        self.load_videos()
        
        # Загрузка заметок
        self.notes_label.setText(player.notes if player.notes else "Нет заметок")
    
    def load_season_stats(self):
        """Загрузка статистики сезона"""
        if not self.player:
            return
        
        # Получение статистики сезона
        season_stats = self.stats_service.get_player_season_stats(self.player.id)
        
        # Отображение статистики
        self.games_label.setText(str(season_stats.get('games', 0)))
        self.goals_label.setText(str(season_stats.get('goals', 0)))
        self.assists_label.setText(str(season_stats.get('assists', 0)))
        self.points_label.setText(str(season_stats.get('points', 0)))
        self.penalty_minutes_label.setText(str(season_stats.get('penalty_minutes', 0)))
        self.plus_minus_label.setText(str(season_stats.get('plus_minus', 0)))
    
    def load_match_stats(self):
        """Загрузка статистики по матчам"""
        if not self.player:
            return
        
        # Получение статистики по матчам
        match_stats = self.stats_service.get_player_match_stats(self.player.id)
        
        # Очистка таблицы
        self.stats_table.setRowCount(0)
        
        # Заполнение таблицы
        for row, stat in enumerate(match_stats):
            self.stats_table.insertRow(row)
            
            # Дата матча
            match_date = format_date(stat['match_date']) if stat['match_date'] else ""
            self.stats_table.setItem(row, 0, QTableWidgetItem(match_date))
            
            # Матч
            match_name = f"{stat['home_team']} - {stat['away_team']}"
            self.stats_table.setItem(row, 1, QTableWidgetItem(match_name))
            
            # Статистика
            self.stats_table.setItem(row, 2, QTableWidgetItem(str(stat['goals'])))
            self.stats_table.setItem(row, 3, QTableWidgetItem(str(stat['assists'])))
            self.stats_table.setItem(row, 4, QTableWidgetItem(str(stat['points'])))
            self.stats_table.setItem(row, 5, QTableWidgetItem(str(stat['plus_minus'])))
            self.stats_table.setItem(row, 6, QTableWidgetItem(str(stat['penalty_minutes'])))
            self.stats_table.setItem(row, 7, QTableWidgetItem(str(stat['shots'])))
            
            # Время на льду
            time_on_ice = ""
            if stat['time_on_ice']:
                minutes = stat['time_on_ice'] // 60
                seconds = stat['time_on_ice'] % 60
                time_on_ice = f"{minutes}:{seconds:02d}"
            self.stats_table.setItem(row, 8, QTableWidgetItem(time_on_ice))
    
    def load_videos(self):
        """Загрузка видеоматериалов"""
        if not self.player:
            return
        
        # Получение видеоматериалов
        videos = self.player_service.get_player_videos(self.player.id)
        
        # Очистка таблицы
        self.video_table.setRowCount(0)
        
        # Заполнение таблицы
        for row, video in enumerate(videos):
            self.video_table.insertRow(row)
            
            self.video_table.setItem(row, 0, QTableWidgetItem(video['title']))
            self.video_table.setItem(row, 1, QTableWidgetItem(format_date(video['date'])))
            self.video_table.setItem(row, 2, QTableWidgetItem(video['type']))
            self.video_table.setItem(row, 3, QTableWidgetItem(video['description'] or ""))
    
    def change_photo(self):
        """Изменение фотографии игрока"""
        if not self.player:
            show_error_message(self, "Ошибка", "Сначала выберите игрока")
            return
        
        # Открытие диалога выбора файла
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбор фотографии игрока",
            "",
            "Изображения (*.jpg *.jpeg *.png)",
            options=options
        )
        
        if file_path:
            try:
                # Обновление фотографии
                self.player_service.update_player_photo(self.player.id, file_path)
                
                # Обновление отображения
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.photo_label.setPixmap(pixmap)
                    self.photo_label.setText("")
                    
                    show_info_message(self, "Информация", "Фотография успешно обновлена")
                else:
                    show_error_message(self, "Ошибка", "Не удалось загрузить изображение")
            except Exception as e:
                show_error_message(self, "Ошибка", f"Не удалось обновить фотографию: {str(e)}")
    
    def add_stats(self):
        """Добавление статистики игрока"""
        if not self.player:
            show_error_message(self, "Ошибка", "Сначала выберите игрока")
            return
        
        # В будущем здесь будет вызов диалога добавления статистики
        QMessageBox.information(self, "Информация", "Функция добавления статистики будет доступна в следующей версии")
    
    def edit_stats(self):
        """Редактирование статистики игрока"""
        if not self.player:
            show_error_message(self, "Ошибка", "Сначала выберите игрока")
            return
        
        # Получение выбранной строки
        selected_rows = self.stats_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Выберите запись для редактирования")
            return
        
        # В будущем здесь будет вызов диалога редактирования статистики
        QMessageBox.information(self, "Информация", "Функция редактирования статистики будет доступна в следующей версии")
    
    def export_stats(self):
        """Экспорт статистики игрока"""
        if not self.player:
            show_error_message(self, "Ошибка", "Сначала выберите игрока")
            return
        
        # В будущем здесь будет реализация экспорта в Excel
        QMessageBox.information(self, "Информация", "Функция экспорта статистики будет доступна в следующей версии")
    
    def show_charts(self):
        """Отображение графиков со статистикой"""
        if not self.player:
            show_error_message(self, "Ошибка", "Сначала выберите игрока")
            return
        
        # В будущем здесь будет реализация отображения графиков
        QMessageBox.information(self, "Информация", "Функция отображения графиков будет доступна в следующей версии")
    
    def add_video(self):
        """Добавление видеоматериала"""
        if not self.player:
            show_error_message(self, "Ошибка", "Сначала выберите игрока")
            return
        
        # В будущем здесь будет вызов диалога добавления видео
        QMessageBox.information(self, "Информация", "Функция добавления видео будет доступна в следующей версии")
    
    def play_video(self):
        """Воспроизведение выбранного видео"""
        if not self.player:
            show_error_message(self, "Ошибка", "Сначала выберите игрока")
            return
        
        # Получение выбранной строки
        selected_rows = self.video_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Выберите видео для просмотра")
            return
        
        # В будущем здесь будет вызов видеоплеера
        QMessageBox.information(self, "Информация", "Функция просмотра видео будет доступна в следующей версии")
    
    def delete_video(self):
        """Удаление выбранного видео"""
        if not self.player:
            show_error_message(self, "Ошибка", "Сначала выберите игрока")
            return
        
        # Получение выбранной строки
        selected_rows = self.video_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Выберите видео для удаления")
            return
        
        # В будущем здесь будет реализация удаления видео
        QMessageBox.information(self, "Информация", "Функция удаления видео будет доступна в следующей версии")
