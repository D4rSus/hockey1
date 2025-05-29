
# -*- coding: utf-8 -*-

"""
Диалог сравнения игроков
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QDialogButtonBox, QGroupBox, QGridLayout,
                           QPushButton, QComboBox, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from services.stats_service import StatsService
from services.player_service import PlayerService
from utils import show_error_message


class PlayerComparisonDialog(QDialog):
    """Диалог для сравнения игроков"""
    
    def __init__(self, team_id, parent=None):
        super().__init__(parent)
        
        self.team_id = team_id
        self.stats_service = StatsService()
        self.player_service = PlayerService()
        self.selected_players = []
        
        self.init_ui()
        self.load_players()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Сравнение игроков")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Панель выбора игроков
        selection_group = QGroupBox("Выбор игроков для сравнения")
        selection_layout = QVBoxLayout(selection_group)
        
        # Добавление игроков
        add_player_layout = QHBoxLayout()
        
        self.player_combo = QComboBox()
        add_player_layout.addWidget(QLabel("Игрок:"))
        add_player_layout.addWidget(self.player_combo)
        
        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self.add_player)
        add_player_layout.addWidget(add_button)
        
        add_player_layout.addStretch()
        
        clear_button = QPushButton("Очистить все")
        clear_button.clicked.connect(self.clear_players)
        add_player_layout.addWidget(clear_button)
        
        selection_layout.addLayout(add_player_layout)
        
        # Список выбранных игроков
        self.selected_players_label = QLabel("Выбранные игроки: нет")
        selection_layout.addWidget(self.selected_players_label)
        
        layout.addWidget(selection_group)
        
        # Таблица сравнения
        comparison_group = QGroupBox("Сравнение статистики")
        comparison_layout = QVBoxLayout(comparison_group)
        
        self.comparison_table = QTableWidget()
        self.comparison_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.comparison_table.setEditTriggers(QTableWidget.NoEditTriggers)
        comparison_layout.addWidget(self.comparison_table)
        
        layout.addWidget(comparison_group)
        
        # График сравнения
        chart_group = QGroupBox("Графическое сравнение")
        chart_layout = QVBoxLayout(chart_group)
        
        # Выбор типа графика
        chart_controls_layout = QHBoxLayout()
        
        chart_controls_layout.addWidget(QLabel("Тип графика:"))
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Основные показатели", "Голы и передачи", "Штрафы и +/-"])
        self.chart_type_combo.currentTextChanged.connect(self.update_chart)
        chart_controls_layout.addWidget(self.chart_type_combo)
        
        chart_controls_layout.addStretch()
        
        chart_layout.addLayout(chart_controls_layout)
        
        # Контейнер для графика
        self.chart_widget = QWidget()
        self.chart_widget.setMinimumSize(600, 300)
        chart_layout.addWidget(self.chart_widget)
        
        layout.addWidget(chart_group)
        
        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_players(self):
        """Загрузка списка игроков команды"""
        try:
            players = self.player_service.get_players(self.team_id)
            
            self.player_combo.clear()
            for player in players:
                self.player_combo.addItem(player.full_name, player.id)
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось загрузить игроков: {str(e)}")
    
    def add_player(self):
        """Добавление игрока в сравнение"""
        player_id = self.player_combo.currentData()
        player_name = self.player_combo.currentText()
        
        if not player_id:
            return
        
        # Проверяем, что игрок еще не добавлен
        if player_id in [p['id'] for p in self.selected_players]:
            show_error_message(self, "Ошибка", "Этот игрок уже добавлен для сравнения")
            return
        
        # Ограничиваем количество игроков для сравнения
        if len(self.selected_players) >= 5:
            show_error_message(self, "Ошибка", "Можно сравнивать не более 5 игроков одновременно")
            return
        
        # Добавляем игрока
        self.selected_players.append({
            'id': player_id,
            'name': player_name
        })
        
        self.update_selected_players_label()
        self.update_comparison_table()
        self.update_chart()
    
    def clear_players(self):
        """Очистка списка выбранных игроков"""
        self.selected_players.clear()
        self.update_selected_players_label()
        self.update_comparison_table()
        self.clear_chart()
    
    def update_selected_players_label(self):
        """Обновление метки с выбранными игроками"""
        if not self.selected_players:
            self.selected_players_label.setText("Выбранные игроки: нет")
        else:
            names = [player['name'] for player in self.selected_players]
            self.selected_players_label.setText(f"Выбранные игроки: {', '.join(names)}")
    
    def update_comparison_table(self):
        """Обновление таблицы сравнения"""
        if not self.selected_players:
            self.comparison_table.setRowCount(0)
            self.comparison_table.setColumnCount(0)
            return
        
        # Получаем статистику для каждого игрока
        players_stats = []
        for player in self.selected_players:
            stats = self.stats_service.get_player_stats(player['id'])
            stats['name'] = player['name']
            players_stats.append(stats)
        
        # Настройка таблицы
        stats_labels = [
            ('Игр', 'games'),
            ('Голы', 'goals'),
            ('Передачи', 'assists'),
            ('Очки', 'points'),
            ('+/-', 'plus_minus'),
            ('Штраф. мин.', 'penalty_minutes'),
            ('Броски', 'shots'),
            ('Время на льду', 'time_on_ice'),
            ('Вбрасывания %', 'faceoff_percentage')
        ]
        
        self.comparison_table.setRowCount(len(stats_labels))
        self.comparison_table.setColumnCount(len(players_stats) + 1)
        
        # Заголовки столбцов
        headers = ['Показатель'] + [player['name'] for player in players_stats]
        self.comparison_table.setHorizontalHeaderLabels(headers)
        
        # Заполнение данных
        for row, (label, key) in enumerate(stats_labels):
            # Название показателя
            self.comparison_table.setItem(row, 0, QTableWidgetItem(label))
            
            # Значения для каждого игрока
            for col, stats in enumerate(players_stats, 1):
                value = stats.get(key, 0)
                if key == 'time_on_ice':
                    # Форматируем время в минуты:секунды
                    minutes = value // 60
                    seconds = value % 60
                    formatted_value = f"{minutes}:{seconds:02d}"
                else:
                    formatted_value = str(value)
                
                item = QTableWidgetItem(formatted_value)
                item.setTextAlignment(Qt.AlignCenter)
                self.comparison_table.setItem(row, col, item)
        
        # Настройка размеров столбцов
        self.comparison_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.comparison_table.verticalHeader().setVisible(False)
    
    def update_chart(self):
        """Обновление графика сравнения"""
        if len(self.selected_players) < 2:
            self.clear_chart()
            return
        
        chart_type = self.chart_type_combo.currentText()
        
        # Получаем статистику игроков
        players_stats = []
        for player in self.selected_players:
            stats = self.stats_service.get_player_stats(player['id'])
            stats['name'] = player['name']
            players_stats.append(stats)
        
        # Очистка контейнера графика
        layout = self.chart_widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        else:
            layout = QVBoxLayout(self.chart_widget)
        
        # Создание графика
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Данные для графика в зависимости от типа
        if chart_type == "Основные показатели":
            categories = ['Игр', 'Очки', 'Броски']
            data_keys = ['games', 'points', 'shots']
        elif chart_type == "Голы и передачи":
            categories = ['Голы', 'Передачи', 'Очки']
            data_keys = ['goals', 'assists', 'points']
        else:  # "Штрафы и +/-"
            categories = ['Штраф. мин.', '+/-', 'Время на льду (мин)']
            data_keys = ['penalty_minutes', 'plus_minus', 'time_on_ice']
        
        # Подготовка данных
        x = np.arange(len(categories))
        width = 0.8 / len(players_stats)
        
        # Отрисовка столбцов для каждого игрока
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for i, stats in enumerate(players_stats):
            values = []
            for key in data_keys:
                value = stats.get(key, 0)
                if key == 'time_on_ice':
                    value = value / 60  # Конвертируем в минуты
                values.append(value)
            
            bars = ax.bar(x + i * width - width * (len(players_stats) - 1) / 2, 
                         values, width, label=stats['name'], 
                         color=colors[i % len(colors)])
            
            # Добавляем значения на столбцы
            for j, bar in enumerate(bars):
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{height:.0f}', ha='center', va='bottom', fontsize=8)
        
        # Настройка графика
        ax.set_xlabel('Показатели')
        ax.set_ylabel('Значения')
        ax.set_title(f'Сравнение игроков: {chart_type}')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        # Добавление графика в виджет
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
    
    def clear_chart(self):
        """Очистка графика"""
        layout = self.chart_widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        else:
            layout = QVBoxLayout(self.chart_widget)
        
        # Добавляем сообщение об отсутствии данных
        no_data_label = QLabel("Выберите хотя бы двух игроков для сравнения")
        no_data_label.setAlignment(Qt.AlignCenter)
        no_data_label.setStyleSheet("color: gray; font-size: 14px;")
        layout.addWidget(no_data_label)
